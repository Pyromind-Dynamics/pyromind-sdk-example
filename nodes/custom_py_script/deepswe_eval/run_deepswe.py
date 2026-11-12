"""Execute pinned Pier trials with independent inference and verifier limits."""

import argparse
import asyncio
import json
import os
from pathlib import Path
import signal
import sys

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS.parent / "coding_eval"))

from atif_export import write_atif
from trajectory_validation import InferenceError, VALIDATED_TRACE, load_trajectory

from pier.models.trial.config import AgentConfig, EnvironmentConfig, TaskConfig, TrialConfig
from pier.trial.trial import Trial


class PipelineTrial(Trial):
    """Validate the trace before releasing inference and starting grading."""

    def __init__(self, config, *, _task=None):
        super().__init__(config, _task=_task)
        # None disables Pier's outer agent deadline; verifier limits remain intact.
        self._execution.agent_timeout_sec = None

    async def run(self):
        self._inference_held = False
        self.failure_stage = "environment"
        await self.inference_slots.acquire()
        self._inference_held = True
        try:
            return await super().run()
        finally:
            self._release_inference()

    def _release_inference(self):
        if self._inference_held:
            self.inference_slots.release()
            self._inference_held = False

    async def _setup_agent(self):
        self.failure_stage = "inference"
        return await super()._setup_agent()

    async def _run_pre_artifacts_script(self):
        if self.result.exception_info is None:
            self.failure_stage = "collection"
        return await super()._run_pre_artifacts_script()

    async def _run_verification(self):
        try:
            # Pier can reach this hook after catching an agent timeout/exit error.
            if self.result.exception_info is not None:
                return
            self.failure_stage = "trajectory"
            document = load_trajectory(
                self.trial_dir, model_name=self.config.agent.model_name,
                run_id=self.run_id,
            )
            write_atif(document, self.trial_dir / "agent" / VALIDATED_TRACE)
        except InferenceError:
            self.failure_stage = "inference"
            raise
        finally:
            self._release_inference()
        self.failure_stage = "grading"
        async with self.grading_slots:
            return await super()._run_verification()


async def run(config):
    inference_slots = asyncio.Semaphore(config["inference_workers"])
    grading_slots = asyncio.Semaphore(config["grading_workers"])
    run_dir = Path(config["run_dir"])
    environment = EnvironmentConfig(
        import_path="pier_runtime:DockerRuntimeEnvironment", delete=True,
        kwargs={"run_dir": str(run_dir), "run_id": config["run_id"],
                "runtime_kind": config["runtime_kind"]},
    )
    agent = AgentConfig(import_path="pier_runtime:HostMiniSweAgent", model_name=config["model_name"])

    async def one(task_path):
        task_id = Path(task_path).name
        trial = None
        try:
            trial = await PipelineTrial.create(TrialConfig(
                task=TaskConfig(path=Path(task_path)), trial_name=task_id,
                trials_dir=run_dir / "trials", agent=agent, environment=environment,
            ))
            trial.inference_slots = inference_slots
            trial.grading_slots = grading_slots
            trial.run_id = config["run_id"]
            result = await trial.run()
            return {"task_id": task_id, "stage": trial.failure_stage,
                    "result": result.model_dump(mode="json")}
        except Exception as exc:
            return {"task_id": task_id, "stage": trial.failure_stage if trial else "environment",
                    "error": f"{type(exc).__name__}: {exc}"}

    pending = [asyncio.create_task(one(path)) for path in config["task_paths"]]
    try:
        results = await asyncio.gather(*pending)
    finally:
        for task in pending:
            if not task.done():
                task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
    (run_dir / "pier-results.json").write_text(json.dumps(results, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Validate tasks and dependencies without running sandboxes")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    if args.check:
        from importlib.metadata import version
        from pier.models.task.task import Task
        from pier.models.task.verifier_mode import resolve_effective_verifier_env_config
        from pier.models.trial.paths import TrialPaths
        from pier_runtime import DockerRuntimeEnvironment
        from minisweagent.models.litellm_model import LitellmModel
        import litellm.responses.mcp.chat_completions_handler
        for path in config["task_paths"]:
            task = Task(task_dir=Path(path))
            if task.has_steps or task.config.verifier.environment_mode.value != "separate":
                raise ValueError("Expected single-step DeepSWE 1.1 tasks with a separate verifier")
            task.paths.test_path.read_bytes()
            for directory, environment_config in [
                (task.paths.environment_dir, task.config.environment),
                (task.paths.tests_dir, resolve_effective_verifier_env_config(task.config, None)),
            ]:
                DockerRuntimeEnvironment(
                    environment_dir=directory, environment_name=Path(path).name,
                    session_id="preflight", trial_paths=TrialPaths(trial_dir=Path("/tmp/deepswe-preflight")),
                    task_env_config=environment_config, run_dir="/tmp", run_id="preflight",
                    runtime_kind="docker",
                )
        print(f"Pier {version('datacurve-pier')}, mini-swe-agent {version('mini-swe-agent')}: "
              f"validated {len(config['task_paths'])} tasks")
        return
    os.environ["DEEPSWE_RUN_CONFIG"] = str(args.config.resolve())
    async def supervised_run():
        loop = asyncio.get_running_loop()
        current = asyncio.current_task()
        loop.add_signal_handler(signal.SIGTERM, current.cancel)
        try:
            await run(config)
        finally:
            loop.remove_signal_handler(signal.SIGTERM)
    asyncio.run(supervised_run())


if __name__ == "__main__":
    main()
