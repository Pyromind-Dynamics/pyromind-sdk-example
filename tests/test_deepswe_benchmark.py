"""DeepSWE contracts, real Mini agent serialization, and pipeline scheduling.

No external model requests, platform resources, or benchmark solutions are used.
"""

import asyncio
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import types
from unittest.mock import Mock

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "nodes/custom_py_script/deepswe_eval"


def load_script(name):
    spec = importlib.util.spec_from_file_location(f"deepswe_test_{name}", SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    paths = sys.path[:]
    try:
        sys.path.insert(0, str(SCRIPTS))
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = paths
    return module


def load_node():
    spec = importlib.util.spec_from_file_location("deepswe_node", SCRIPTS / "eval_benchmark.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def task(root, name):
    path = root / name
    (path / "tests").mkdir(parents=True)
    (path / "task.toml").write_text('[verifier]\nenvironment_mode="separate"\n')
    (path / "instruction.md").write_text("Synthetic task")
    (path / "tests/test.sh").write_text("exit 0\n")
    return path


def native(task_id):
    return {
        "trajectory_format": "mini-swe-agent-1.1", "instance_id": task_id,
        "info": {"mini_version": "2.4.6", "exit_status": "Submitted"},
        "messages": [{"role": "user", "content": "Synthetic task"},
                     {"role": "assistant", "content": "Synthetic answer"}],
    }


def report(root, task_id, reward, *, error=None, with_trajectory=True):
    result = {"verifier_result": {"rewards": {"reward": reward}}}
    if error:
        result["exception_info"] = {"exception_type": "SyntheticError", "exception_message": error}
    if with_trajectory:
        path = root / "trials" / task_id / "agent/mini-swe-agent.trajectory.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(native(task_id)))
    return {"task_id": task_id, "result": result}


def prepare_reports(root, entries):
    (root / "pier-results.json").write_text(json.dumps(entries))
    (root / "run-config.json").write_text(json.dumps({"runtime_kind": "pyromind", "dataset_revision": "synthetic"}))


def test_node_loads_with_existing_configuration_ports():
    from pyromind_sdk.nodes.yaml_loader import create_node_class_from_yaml
    path = ROOT / "nodes/deepsweBenchmark.yaml"
    data = yaml.safe_load(path.read_text())
    node = create_node_class_from_yaml(data, class_name=data["name"], yaml_file_path=str(path), strict=True)
    assert set(node.INPUT_TYPES()["required"]) == {"inference_config", "rollout_config", "pyromind_api_key", "output_dir"}
    assert node.RETURN_NAMES == ("output_file_path",)
    for source, name in [("InferenceConfig.yaml", "inference_config"), ("RolloutConfig.yaml", "rollout_config")]:
        outputs = yaml.safe_load((ROOT / "nodes" / source).read_text())["parameters"]
        assert next(p for p in outputs if p["name"] == name)["dtype"] == "STRING"


def test_task_selection_uses_stable_slice_and_rejects_old_verifiers(tmp_path):
    node = load_node()
    for name in ("c", "a", "b"):
        task(tmp_path, name)
    assert [p.name for p in node.select_tasks(tmp_path, 2, 1)] == ["b", "c"]
    (tmp_path / "b/task.toml").write_text('[verifier]\nenvironment_mode="shared"\n')
    with pytest.raises(ValueError, match="separate-verifier"):
        node.select_tasks(tmp_path, 1, 1)
    with pytest.raises(ValueError, match="No DeepSWE tasks"):
        node.select_tasks(tmp_path, 1, 99)


@pytest.mark.parametrize("reward", [-1, None, True, 0.5])
def test_invalid_reward_is_not_reported_as_a_model_zero(tmp_path, reward):
    node = load_node()
    prepare_reports(tmp_path, [report(tmp_path, "task", reward)])
    node.export_results(tmp_path, ["task"], "synthetic", "run")
    result = json.loads((tmp_path / "benchmark.json").read_text())
    assert result["tasks"]["task"]["score"] is None
    assert result["tasks"]["task"]["status"] == "failed"
    assert result["summary"]["scored_tasks"] == 0
    assert result["summary"]["mean_score"] is None


def test_scores_failures_and_atif_are_exported_separately(tmp_path):
    from harbor.models.trajectories.trajectory import Trajectory
    node = load_node()
    prepare_reports(tmp_path, [report(tmp_path, "pass", 1), report(tmp_path, "zero", 0),
                              report(tmp_path, "error", None, error="Infrastructure unavailable", with_trajectory=False)])
    path = node.export_results(tmp_path, ["pass", "zero", "error"], "synthetic", "run")
    result = json.loads(path.read_text())
    assert result["benchmark"] == "DeepSWE 1.1"
    assert result["summary"] == {"total_tasks": 3, "scored_tasks": 2, "failed_tasks": 1,
                                 "resolved_tasks": 1, "mean_score": 0.5}
    assert result["tasks"][2]["score"] is None
    assert result["tasks"][2]["output_file_path"] is None
    for item in result["tasks"][:2]:
        doc = json.loads(Path(item["output_file_path"]).read_text())
        Trajectory.model_validate(doc)
        assert doc["final_metrics"]["extra"]["benchmark"]["name"] == "DeepSWE 1.1"


def test_single_task_returns_valid_atif(tmp_path):
    node = load_node()
    prepare_reports(tmp_path, [report(tmp_path, "one", 0)])
    output = node.export_results(tmp_path, ["one"], "synthetic", "run")
    assert output.name == "trajectory.atif.json"
    assert json.loads(output.read_text())["schema_version"] == "ATIF-v1.8"


@pytest.mark.parametrize("problem", ["missing", "malformed", "wrong_task", "no_agent", "inference_error"])
def test_bad_trace_is_unscored_even_if_an_old_reward_exists(tmp_path, problem):
    node = load_node()
    entry = report(tmp_path, "one", 1, with_trajectory=problem != "missing")
    path = tmp_path / "trials/one/agent/mini-swe-agent.trajectory.json"
    if problem == "malformed":
        path.write_text("{broken")
    elif problem != "missing":
        data = native("different" if problem == "wrong_task" else "one")
        if problem == "no_agent":
            data["messages"] = data["messages"][:1]
        if problem == "inference_error":
            data["info"].update(exit_status="RuntimeError", exception_str="model request failed")
        path.write_text(json.dumps(data))
    prepare_reports(tmp_path, [entry])
    output = node.export_results(tmp_path, ["one"], "synthetic", "run")
    result = json.loads(output.read_text())
    assert output.name == "manifest.json"
    assert result["summary"] == {"total_tasks": 1, "scored_tasks": 0, "failed_tasks": 1,
                                 "resolved_tasks": 0, "mean_score": None}
    assert result["tasks"][0]["score"] is None
    assert result["tasks"][0]["resolved"] is None
    assert result["failed_tasks"]["one"]["stage"] == (
        "inference" if problem == "inference_error" else "trajectory")
    assert json.loads((tmp_path / "benchmark.json").read_text())["tasks"]["one"]["status"] == "failed"


def test_environment_error_is_not_replaced_by_missing_trace(tmp_path):
    node = load_node()
    entry = report(tmp_path, "one", None, error="sandbox startup timed out", with_trajectory=False)
    entry["stage"] = "environment"
    prepare_reports(tmp_path, [entry])
    output = node.export_results(tmp_path, ["one"], "synthetic", "run")
    failure = json.loads(output.read_text())["failed_tasks"]["one"]
    assert failure["stage"] == "environment"
    assert "sandbox startup timed out" in failure["error"]


def test_final_output_write_error_aborts_instead_of_counting_twice(tmp_path, monkeypatch):
    node = load_node()
    prepare_reports(tmp_path, [report(tmp_path, "one", 1)])
    monkeypatch.setattr(node, "write_atif", Mock(side_effect=OSError("disk full")))
    with pytest.raises(OSError, match="disk full"):
        node.export_results(tmp_path, ["one"], "synthetic", "run")
    assert not (tmp_path / "benchmark.json").exists()


def test_node_never_persists_keys_and_cleans_up_on_runner_error(tmp_path, monkeypatch):
    node = load_node()
    task(tmp_path / "dataset", "one")
    with (tmp_path / "dataset/one/task.toml").open("a") as config_file:
        config_file.write('[agent]\ntimeout_sec=321\n')
    monkeypatch.setenv("DEEPSWE_TASKS", str(tmp_path / "dataset"))
    monkeypatch.delenv("DEEPSWE_DOCKER_HOST", raising=False)
    monkeypatch.setenv("MSWEA_API_KEY", "wrong-inherited-key")
    monkeypatch.setattr(node, "runtime_python", lambda: Path(sys.executable))
    monkeypatch.setattr(node.subprocess, "run", Mock(return_value=Mock(returncode=1, stdout="")))
    prepare = Mock(return_value="unix:///owned.sock")
    stop = Mock()
    monkeypatch.setattr(node, "prepare_docker_context", prepare)
    monkeypatch.setattr(node, "stop_docker_context", stop)
    def fail(command, environment, log_path):
        assert environment["OPENAI_API_KEY"] == "synthetic-model-key"
        assert "MSWEA_API_KEY" not in environment
        assert environment["DOCKER_HOST"] == "unix:///owned.sock"
        raise RuntimeError("synthetic runner failure")
    monkeypatch.setattr(node, "launch_runner", fail)
    with pytest.raises(RuntimeError, match="synthetic runner failure"):
        node.eval_deepswe_benchmark(
            json.dumps({"endpoint": "https://service.example/v1", "model_name": "model", "api_key": "synthetic-model-key"}),
            json.dumps({"num_tasks": 1, "start_index": 0, "inference_workers": 1, "grading_workers": 1}),
            "synthetic-platform-key", str(tmp_path / "output"),
        )
    stop.assert_called_once()
    saved = next((tmp_path / "output").glob("*/run-config.json")).read_text()
    assert json.loads(saved)["agent_timeouts"] == {"one": 321}
    assert "synthetic-model-key" not in saved
    assert "synthetic-platform-key" not in saved


def test_pipeline_overlaps_inference_and_grading_with_independent_limits(monkeypatch):
    pytest.importorskip("pier")
    runner = load_script("run_deepswe")
    from pier.trial.trial import Trial
    monkeypatch.setattr(runner, "load_trajectory", Mock(return_value={}))
    monkeypatch.setattr(runner, "write_atif", Mock())
    async def exercise():
        inference = asyncio.Semaphore(2)
        grading = asyncio.Semaphore(1)
        active = {"inference": 0, "grading": 0}
        peak = {"inference": 0, "grading": 0}
        grading_started = asyncio.Event()
        overlapped = asyncio.Event()
        async def verify(self):
            active["grading"] += 1
            peak["grading"] = max(peak["grading"], active["grading"])
            grading_started.set()
            await asyncio.sleep(0.02)
            active["grading"] -= 1
        async def run(self):
            active["inference"] += 1
            peak["inference"] = max(peak["inference"], active["inference"])
            if self.index >= 2:
                await grading_started.wait()
                if active["grading"]:
                    overlapped.set()
            await asyncio.sleep(0.01)
            active["inference"] -= 1
            await self._run_verification()
        monkeypatch.setattr(Trial, "run", run)
        monkeypatch.setattr(Trial, "_run_verification", verify)
        trials = []
        for i in range(6):
            trial = object.__new__(runner.PipelineTrial)
            trial.inference_slots, trial.grading_slots, trial.index = inference, grading, i
            trial._result = Mock(exception_info=None)
            trial.config = types.SimpleNamespace(trials_dir=Path("/unused"), trial_name=str(i),
                                                 agent=types.SimpleNamespace(model_name="synthetic"))
            trial.run_id = "run"
            trials.append(trial)
        await asyncio.wait_for(asyncio.gather(*(t.run() for t in trials)), 5)
        assert peak == {"inference": 2, "grading": 1}
        assert overlapped.is_set()
        assert inference._value == 2 and grading._value == 1
    asyncio.run(exercise())


@pytest.mark.parametrize("commit_changes", [True, False])
def test_real_mini_agent_owns_submission_without_automatic_staging(tmp_path, monkeypatch, commit_changes):
    run_agent = load_script("run_agent")
    import litellm
    from minisweagent.models.litellm_model import LitellmModel
    from atif_export import convert_to_atif
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test", "-c", "user.email=test@localhost",
                    "commit", "--allow-empty", "-qm", "base"], check=True)
    base = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()
    class LocalAttached(run_agent.AttachedEnvironment):
        def execute(self, action, cwd=""):
            process = subprocess.run(["bash", "-c", action["command"]], cwd=repo,
                                     text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = process.stdout
            if action["command"] == "git rev-parse --verify HEAD":
                output = " \r\n" + output + "\n"
            result = {"output": output, "returncode": process.returncode, "exception_info": ""}
            self._check_finished(result)
            return result
    command = "printf 'fixed\\n' > value.txt && printf '\\000build' > compiled-output && cp value.txt value.txt.bak && "
    if commit_changes:
        command += ("git add value.txt && git -c user.name=Test -c user.email=test@localhost "
                    "commit -qm 'Agent selected change' && ")
    command += "echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"
    response = litellm.ModelResponse(model="openai/synthetic", choices=[{"finish_reason": "tool_calls", "message": {
        "role": "assistant", "content": "Make the requested synthetic change.",
        "tool_calls": [{"id": "call", "type": "function", "function": {"name": "bash", "arguments": json.dumps({
            "command": command
        })}}],
    }}], usage={"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20})
    model = LitellmModel(model_name="openai/synthetic", cost_tracking="ignore_errors",
                         model_kwargs={"mock_response": response, "custom_llm_provider": "openai"})
    def make_model(*, config):
        model.config.observation_template = config["observation_template"]
        return model
    monkeypatch.setattr(run_agent, "get_model", make_model)
    monkeypatch.setattr(run_agent, "AttachedEnvironment", LocalAttached)
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"model_name": "synthetic", "endpoint": "http://127.0.0.1:1/v1",
                                  "agent_timeouts": {"one": 120}}))
    instruction = tmp_path / "instruction.txt"
    instruction.write_text("Write fixed to value.txt")
    trajectory = tmp_path / "native.json"
    monkeypatch.setattr(sys, "argv", ["run_agent", "--config", str(config), "--instruction", str(instruction),
                                      "--container", "synthetic", "--trajectory", str(trajectory), "--task-id", "one"])
    run_agent.main()
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          check=True, capture_output=True, text=True).stdout.strip()
    diff = subprocess.run(["git", "-C", str(repo), "diff", "--name-only", base, "HEAD"],
                          check=True, capture_output=True, text=True).stdout.splitlines()
    assert diff == (["value.txt"] if commit_changes else [])
    staged = subprocess.run(["git", "-C", str(repo), "diff", "--cached", "--name-only"],
                            check=True, capture_output=True, text=True).stdout
    assert staged == "", "The evaluator must not stage any leftover files"
    assert (head != base) is commit_changes
    assert (repo / "compiled-output").read_bytes() == b"\0build"
    assert (repo / "value.txt.bak").exists()
    submission = json.loads((tmp_path / "submission.json").read_text())
    assert submission["has_new_commit"] is commit_changes
    assert submission["initial_commit"] == base and submission["submitted_commit"] == head
    assert "compiled-output" in submission["worktree_status"]
    assert "value.txt.bak" in submission["worktree_status"]
    assert submission["committed_files"] == ("A\tvalue.txt" if commit_changes else "")
    saved = json.loads(trajectory.read_text())
    assert saved["info"]["exit_status"] == "Submitted"
    assert saved["info"]["config"]["agent"]["step_limit"] == 0
    assert saved["info"]["config"]["agent"]["wall_time_limit_seconds"] == 120
    assert "git diff" in saved["messages"][0]["content"]
    assert "will not commit files for you" in saved["messages"][0]["content"]
    doc = convert_to_atif(saved, task_id="one", model_name="synthetic",
                          session_id="run", benchmark={"name": "DeepSWE 1.1", "task_id": "one", "score": 1})
    assert doc["schema_version"] == "ATIF-v1.8"


def test_submission_diagnostics_survive_invalid_commit(tmp_path):
    agent = load_script("run_agent")
    environment = Mock()
    environment.execute.side_effect = [
        {"returncode": 0, "output": "truncated-commit\n"},
        {"returncode": 0, "output": " M source.py\n"},
    ]
    path = tmp_path / "submission.json"
    agent.record_submission(environment, path, "a" * 40)
    result = json.loads(path.read_text())
    assert result["submitted_commit"] is None
    assert result["has_new_commit"] is None
    assert result["worktree_status"] == " M source.py"
    assert "Invalid Git commit" in result["diagnostic_errors"]["submitted_commit"]
    assert all("git diff" not in c.args[0]["command"] for c in environment.execute.call_args_list)


def test_official_observation_truncation_and_nonretryable_bad_request(tmp_path, monkeypatch):
    agent = load_script("run_agent")
    import litellm
    from minisweagent.models.litellm_model import LitellmModel
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"model_name": "synthetic", "endpoint": "http://127.0.0.1:1/v1"}))
    instruction = tmp_path / "instruction.txt"
    instruction.write_text("Synthetic output test")
    trace = tmp_path / "native.json"
    monkeypatch.setattr(sys, "argv", ["run_agent", "--config", str(config_path), "--instruction", str(instruction),
                                      "--container", "synthetic", "--trajectory", str(trace), "--task-id", "one"])
    model = None
    def make_model(*, config):
        nonlocal model
        model = LitellmModel(**{k: v for k, v in config.items() if k != "model_class"})
        return model
    monkeypatch.setattr(agent, "get_model", make_model)
    raw_output = "HEAD:" + "x" * 3_000_000 + ":TAIL"
    environment = agent.AttachedEnvironment("synthetic")
    environment.execute = Mock(side_effect=[
        {"returncode": 0, "output": "a" * 40 + "\n"},
        {"returncode": 0, "output": raw_output, "exception_info": ""},
        {"returncode": 0, "output": "a" * 40 + "\n"},
        {"returncode": 0, "output": ""},
        {"returncode": 0, "output": ""},
        {"returncode": 0, "output": ""},
    ])
    monkeypatch.setattr(agent, "AttachedEnvironment", lambda _: environment)
    response = litellm.ModelResponse(model="openai/synthetic", choices=[{"finish_reason": "tool_calls", "message": {
        "role": "assistant", "content": "Read synthetic output",
        "tool_calls": [{"id": "call", "type": "function", "function": {"name": "bash", "arguments": '{"command":"synthetic"}'}}],
    }}], usage={"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20})
    request_error = litellm.exceptions.BadRequestError(message="Range of input length", model="synthetic", llm_provider="openai")
    calls = Mock(side_effect=[response, request_error])
    monkeypatch.setattr(litellm, "completion", calls)
    with pytest.raises(litellm.exceptions.BadRequestError):
        agent.main()
    assert calls.call_count == 2, "Do not retry a deterministic HTTP 400"
    sent = calls.call_args_list[1].kwargs["messages"]
    observation = json.loads(next(m["content"] for m in sent if m["role"] == "tool"))
    assert len(observation["output_head"]) == len(observation["output_tail"]) == 5000
    assert observation["elided_chars"] == len(raw_output) - 10000
    assert sum(len(m.get("content") or "") for m in sent) < 20000
    saved = json.loads(trace.read_text())
    assert saved["info"]["exception_str"] == str(request_error)
    assert next(m["extra"]["raw_output"] for m in saved["messages"] if m["role"] == "tool") == raw_output


@pytest.mark.parametrize("runtime_kind", ["pyromind", "docker"])
def test_empty_artifacts_are_uploaded_without_zero_chunk_requests(tmp_path, runtime_kind):
    pytest.importorskip("pier")
    runtime = load_script("pier_runtime")
    from pier.environments.base import ExecResult
    environment = object.__new__(runtime.DockerRuntimeEnvironment)
    environment.runtime_kind, environment.container_id = runtime_kind, "synthetic"
    source, target = tmp_path / "source", tmp_path / "target with spaces"
    (source / "nested").mkdir(parents=True)
    (source / "model.patch").touch()
    (source / "nested/empty.txt").touch()
    (source / "nested/nonempty.txt").write_text("keep")
    (source / "empty-dir").mkdir()
    target.mkdir()
    (target / "model.patch").write_text("stale contents")
    async def execute(command):
        result = subprocess.run(["bash", "-c", command], capture_output=True, text=True)
        return ExecResult(stdout=result.stdout, stderr=result.stderr, return_code=result.returncode)
    async def checked(*args):
        assert args[0] == "cp"
        path = Path(args[1].removesuffix("/."))
        destination = Path(args[2].split(":", 1)[1])
        if runtime_kind == "pyromind":
            assert not (path.is_file() and path.stat().st_size == 0), "Reproduces zero-chunk API rejection"
            assert not (path.is_dir() and any(p.is_file() and not p.stat().st_size for p in path.rglob("*")))
        if path.is_dir():
            shutil.copytree(path, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(path, destination)
    environment.exec, environment._checked = execute, checked
    asyncio.run(environment.upload_dir(source, str(target)))
    assert (target / "model.patch").read_bytes() == b""
    assert (target / "nested/empty.txt").read_bytes() == b""
    assert (target / "nested/nonempty.txt").read_text() == "keep"
    assert (target / "empty-dir").is_dir()


@pytest.mark.parametrize("host,server_version", [(None, None), ("unix:///rt.sock", "24.0.0-docker-rt")])
def test_strict_isolation_rejects_unsupported_platform_before_starting(tmp_path, monkeypatch, host, server_version):
    node = load_node()
    task(tmp_path / "dataset", "one")
    monkeypatch.setenv("DEEPSWE_TASKS", str(tmp_path / "dataset"))
    monkeypatch.setenv("DEEPSWE_REQUIRE_NETWORK_ISOLATION", "1")
    if host:
        monkeypatch.setenv("DEEPSWE_DOCKER_HOST", host)
    else:
        monkeypatch.delenv("DEEPSWE_DOCKER_HOST", raising=False)
    monkeypatch.setattr(node, "runtime_python", lambda: Path(sys.executable))
    monkeypatch.setattr(node.subprocess, "run", Mock(return_value=Mock(stdout=server_version)))
    prepare = Mock(side_effect=AssertionError("must not provision a sandbox"))
    monkeypatch.setattr(node, "prepare_docker_context", prepare)
    with pytest.raises(RuntimeError, match="network isolation"):
        node.eval_deepswe_benchmark(
            json.dumps({"endpoint": "https://service.example/v1", "model_name": "synthetic"}),
            json.dumps({"inference_workers": 1, "grading_workers": 1}), "synthetic", str(tmp_path / "output"))
    prepare.assert_not_called()


@pytest.mark.parametrize("trace_state", ["valid", "empty_patch", "missing", "malformed", "inference_error", "agent_exit_error", "environment_error", "write_error"])
def test_pier_collects_patch_and_grades_in_a_pristine_separate_environment(tmp_path, monkeypatch, trace_state):
    pytest.importorskip("pier")
    runtime = load_script("pier_runtime")
    runner = load_script("run_deepswe")
    from pier.agents.base import BaseAgent
    from pier.environments.base import ExecResult
    from pier.models.trial.config import AgentConfig, EnvironmentConfig, TaskConfig, TrialConfig
    image = tmp_path / "image"
    image.mkdir()
    (image / "value.txt").write_text("base\n")
    def git(*args):
        return subprocess.run(["git", "-C", str(image), *args], check=True, capture_output=True, text=True)
    git("init", "-q")
    git("add", ".")
    git("-c", "user.name=Test", "-c", "user.email=test@localhost", "commit", "-qm", "base")
    base_sha = git("rev-parse", "HEAD").stdout.strip()
    path = tmp_path / "synthetic-task"
    (path / "environment").mkdir(parents=True)
    (path / "tests").mkdir()
    (path / "instruction.md").write_text("Change value.txt from base to fixed")
    (path / "task.toml").write_text(
        'schema_version="1.3"\nartifacts=["/logs/artifacts/model.patch"]\n'
        '[environment]\ndocker_image="synthetic-image"\nnetwork_mode="no-network"\n'
        '[verifier]\nenvironment_mode="separate"\nnetwork_mode="no-network"\n'
        '[verifier.environment]\ncpus=1\n'
        '[[verifier.collect]]\ncommand="cd /app && git diff --binary '
        + base_sha + ' HEAD > /logs/artifacts/model.patch"\n'
    )
    (path / "tests/Dockerfile").write_text('FROM synthetic-image\nCOPY test.sh /tests/test.sh\n')
    (path / "tests/test.sh").write_text(
        '#!/bin/bash\nset -eu\nSANDBOX_ROOT="$(cd "$(dirname "$0")/.." && pwd)"\ncd "$SANDBOX_ROOT/app"\n'
        'test "$(cat value.txt)" = base\n'
        'if [ ! -s "$SANDBOX_ROOT/logs/artifacts/model.patch" ]; then\n'
        "  echo '{\"reward\":0}' > \"$SANDBOX_ROOT/logs/verifier/reward.json\"\n  exit 0\nfi\n"
        'git apply "$SANDBOX_ROOT/logs/artifacts/model.patch"\n'
        'test "$(cat value.txt)" = fixed\n'
        "echo '{\"reward\":1}' > \"$SANDBOX_ROOT/logs/verifier/reward.json\"\n"
    )
    roots, deleted, commands = {}, [], []
    class SyntheticEnvironment(runtime.DockerRuntimeEnvironment):
        async def _docker(self, *args, timeout=300):
            args = list(map(str, args))
            if args[0] == "run":
                if trace_state == "environment_error":
                    raise RuntimeError("sandbox startup timed out")
                if self.is_verifier:
                    cached = tmp_path / "trials/synthetic-task/agent/trajectory.atif.json"
                    assert cached.is_file(), "Trajectory must be converted and saved before starting the verifier"
                container = args[args.index("--name") + 1]
                root = tmp_path / container
                root.mkdir()
                shutil.copytree(image, root / "app")
                roots[container] = root
                Path(args[args.index("--cidfile") + 1]).write_text(container)
                if trace_state != "empty_patch":
                    assert args[args.index("--network") + 1] == "none"
                return ExecResult(stdout=container, stderr="", return_code=0)
            if args[0] == "rm":
                deleted.append(args[-1])
                shutil.rmtree(roots[args[-1]])
                return ExecResult(stdout="", stderr="", return_code=0)
            if args[0] == "cp":
                source, target = args[1:]
                uploading = any(target.startswith(container + ":") for container in roots)
                for container, root in roots.items():
                    if source.startswith(container + ":"):
                        source = str(root / source.split(":", 1)[1].lstrip("/"))
                    if target.startswith(container + ":"):
                        target = str(root / target.split(":", 1)[1].lstrip("/"))
                if Path(source).is_dir():
                    if trace_state == "empty_patch" and uploading:
                        assert not any(p.is_file() and p.stat().st_size == 0 for p in Path(source).rglob("*")), "zero-chunk upload"
                    shutil.copytree(source, target, dirs_exist_ok=True)
                else:
                    if trace_state == "empty_patch" and uploading:
                        assert Path(source).stat().st_size > 0, "zero-chunk upload"
                    shutil.copy2(source, target)
                return ExecResult(stdout="", stderr="", return_code=0)
            assert args[0] == "exec"
            if args[-2:] == ["id", "-u"]:
                return ExecResult(stdout="0\n", stderr="", return_code=0)
            container = next(arg for arg in args[1:] if arg in roots)
            root = roots[container]
            command = args[-1]
            commands.append((container, command))
            for prefix in ("/app", "/logs", "/tests", "/solution"):
                command = command.replace(prefix, str(root / prefix.lstrip("/")))
            cwd = root / args[args.index("--workdir") + 1].lstrip("/")
            result = subprocess.run(["bash", "-c", command], cwd=cwd, capture_output=True, text=True)
            return ExecResult(stdout=result.stdout, stderr=result.stderr, return_code=result.returncode)
    class SyntheticAgent(BaseAgent):
        @staticmethod
        def name():
            return "synthetic-agent"
        def version(self):
            return "test"
        async def setup(self, environment):
            pass
        async def run(self, instruction, environment, context):
            root = roots[environment.container_id]
            assert not (root / "tests/test.sh").exists(), "Hidden tests must not be uploaded to the agent"
            if trace_state != "empty_patch":
                result = await environment.exec(
                    "printf 'fixed\\n' > value.txt && git add value.txt && "
                    "git -c user.name=Test -c user.email=test@localhost commit -qm fix"
                )
                assert result.return_code == 0
            self.logs_dir.mkdir(parents=True, exist_ok=True)
            data = native("synthetic-task")
            if trace_state == "inference_error":
                data["info"].update(exception_str="model request failed", exit_status="RuntimeError")
            if trace_state != "missing":
                (self.logs_dir / "mini-swe-agent.trajectory.json").write_text(
                    "{broken" if trace_state == "malformed" else json.dumps(data))
            if trace_state == "agent_exit_error":
                from pier.agents.installed.base import NonZeroAgentExitCodeError
                raise NonZeroAgentExitCodeError("agent subprocess failed")
    module = types.ModuleType("deepswe_synthetic_runtime")
    module.Environment, module.Agent = SyntheticEnvironment, SyntheticAgent
    monkeypatch.setitem(sys.modules, module.__name__, module)
    if trace_state == "write_error":
        monkeypatch.setattr(runner, "write_atif", Mock(side_effect=OSError("disk full")))
    async def exercise():
        trial = await runner.PipelineTrial.create(TrialConfig(
            task=TaskConfig(path=path), trial_name="synthetic-task", trials_dir=tmp_path / "trials",
            agent=AgentConfig(import_path="deepswe_synthetic_runtime:Agent", model_name="synthetic"),
            environment=EnvironmentConfig(import_path="deepswe_synthetic_runtime:Environment",
                kwargs={"run_dir": str(tmp_path), "run_id": "test",
                        "runtime_kind": "pyromind" if trace_state == "empty_patch" else "docker"}),
        ))
        trial.inference_slots = asyncio.Semaphore(1)
        trial.grading_slots = asyncio.Semaphore(1)
        trial.run_id = "test"
        result = await trial.run()
        assert trial.inference_slots._value == 1 and trial.grading_slots._value == 1
        if trace_state in {"valid", "empty_patch"}:
            assert result.exception_info is None, result.exception_info
            assert result.verifier_result.rewards["reward"] == (0 if trace_state == "empty_patch" else 1)
            assert (trial.trial_dir / "agent/trajectory.atif.json").is_file()
        else:
            assert result.exception_info is not None
            assert result.verifier_result is None
            assert trial.failure_stage == {"environment_error": "environment", "inference_error": "inference",
                                          "agent_exit_error": "inference"}.get(
                trace_state, "trajectory")
        return result, trial.failure_stage
    result, stage = asyncio.run(exercise())
    expected_containers = 2 if trace_state in {"valid", "empty_patch"} else 0 if trace_state == "environment_error" else 1
    assert len(roots) == len(deleted) == expected_containers
    assert (image / "value.txt").read_text() == "base\n"
    assert (tmp_path / "trials/synthetic-task/artifacts/model.patch").is_file() == (trace_state != "environment_error")
    prepare_reports(tmp_path, [{"task_id": "synthetic-task", "stage": stage, "result": result.model_dump(mode="json")}])
    node = load_node()
    node.export_results(tmp_path, ["synthetic-task"], "synthetic", "test")
    summary = json.loads((tmp_path / "benchmark.json").read_text())["summary"]
    assert summary["total_tasks"] == summary["scored_tasks"] + summary["failed_tasks"] == 1
    assert summary["scored_tasks"] == (1 if trace_state in {"valid", "empty_patch"} else 0)
    if trace_state in {"valid", "empty_patch"}:
        doc = json.loads((tmp_path / "trajectory.atif.json").read_text())
        assert doc["final_metrics"]["extra"]["benchmark"]["score"] == (0 if trace_state == "empty_patch" else 1)


def test_host_agent_process_timeout_follows_selected_task(tmp_path, monkeypatch):
    pytest.importorskip("pier")
    runtime = load_script("pier_runtime")
    from pier.environments.base import ExecResult
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"agent_timeouts": {"one": 321}}))
    monkeypatch.setenv("DEEPSWE_RUN_CONFIG", str(config))
    calls = []
    async def process(*args, **kwargs):
        calls.append(kwargs)
        path = Path(args[args.index("--trajectory") + 1])
        path.write_text(json.dumps(native("one")))
        return ExecResult(stdout="", stderr="", return_code=0)
    monkeypatch.setattr(runtime, "run_process", process)
    agent = runtime.HostMiniSweAgent(logs_dir=tmp_path / "one/agent", model_name="synthetic")
    context = types.SimpleNamespace()
    asyncio.run(agent.run("Synthetic instruction", types.SimpleNamespace(container_id="synthetic"), context))
    assert calls[0]["timeout"] == 381
    assert context.n_agent_steps == 1


@pytest.mark.parametrize("kind,cpus,memory_mb,expected_cpu,expected_memory", [
    ("pyromind", 2, 8192, 4, 8192),
    ("pyromind", 4, 4096, 4, 8192),
    ("pyromind", 1, 3072, 2, 4096),
    ("docker", 2, 8192, 2, 8192),
])
def test_sandbox_resource_requests_fit_platform_without_reducing_task_limits(
    tmp_path, monkeypatch, kind, cpus, memory_mb, expected_cpu, expected_memory,
):
    pytest.importorskip("pier")
    runtime = load_script("pier_runtime")
    from pier.environments.base import ExecResult
    from pier.models.task.config import EnvironmentConfig
    from pier.models.trial.paths import TrialPaths
    environment_dir = tmp_path / "environment"
    environment_dir.mkdir()
    task_config = EnvironmentConfig(docker_image="synthetic-image", cpus=cpus, memory_mb=memory_mb)
    environment = runtime.DockerRuntimeEnvironment(
        environment_dir=environment_dir, environment_name="synthetic", session_id="test",
        trial_paths=TrialPaths(trial_dir=tmp_path / "trial"), task_env_config=task_config,
        run_dir=str(tmp_path), run_id="test", runtime_kind=kind,
    )
    requests = []
    async def docker(*args, timeout=300):
        if args[0] == "run":
            requests.append(args)
            allocated_cpu = int(args[args.index("--cpus") + 1])
            allocated_memory = int(args[args.index("--memory") + 1].removesuffix("m"))
            if kind == "pyromind":
                assert allocated_memory == allocated_cpu * 2048, "Platform rejects other ratios"
            assert allocated_cpu >= cpus and allocated_memory >= memory_mb
            return ExecResult(stdout="f" * 64, stderr="", return_code=0)
        return ExecResult(stdout="", stderr="", return_code=0)
    monkeypatch.setattr(environment, "_docker", docker)
    async def exercise():
        await environment.start()
        await environment.stop()
    asyncio.run(exercise())
    args = requests[0]
    assert args[args.index("--cpus") + 1] == str(expected_cpu)
    assert args[args.index("--memory") + 1] == f"{expected_memory}m"
    metadata = json.loads((tmp_path / "trial/resources-agent.json").read_text())
    assert metadata["requested"] == {"cpus": cpus, "memory_mb": memory_mb}
    assert metadata["allocated"] == {"cpus": expected_cpu, "memory_mb": expected_memory}
    assert task_config.cpus == cpus and task_config.memory_mb == memory_mb
