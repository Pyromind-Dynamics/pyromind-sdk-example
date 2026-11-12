"""DeepSWE 1.1 workflow node: mini-swe-agent, Pier verification, ATIF-v1.8."""

import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
from urllib.parse import urlsplit
from uuid import uuid4

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS.parent / "coding_eval"))
from atif_export import trajectory_model, write_atif
from docker_ctx_prep import prepare_docker_context, stop_docker_context, _remove_sandbox_containers
from trajectory_validation import InferenceError, load_validated_trajectory


def select_tasks(tasks_dir: Path, num_tasks: int, start_index: int) -> list[Path]:
    tasks = sorted(path for path in tasks_dir.iterdir() if path.is_dir() and (path / "task.toml").is_file())
    selected = tasks[start_index:start_index + num_tasks]
    if not selected:
        raise ValueError(f"No DeepSWE tasks selected (available={len(tasks)}, start_index={start_index})")
    return selected


def runtime_python() -> Path:
    override = os.environ.get("DEEPSWE_PYTHON")
    return (Path(override).expanduser() if override else
            Path.home() / ".local/share/uv/tools/datacurve-pier/bin/python")


def runner_environment(api_key: str, docker_host: str | None = None) -> dict:
    environment = os.environ.copy()
    environment["OPENAI_API_KEY"] = api_key.strip()
    environment.pop("MSWEA_API_KEY", None)
    environment["MSWEA_CONFIGURED"] = "true"
    environment["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"
    environment["TTY_COMPATIBLE"] = "0"
    environment["PATH"] = f"/usr/local/bin{os.pathsep}{environment.get('PATH', '')}"
    environment["PYTHONPATH"] = os.pathsep.join([
        str(SCRIPTS), str(SCRIPTS.parent / "coding_eval"), environment.get("PYTHONPATH", ""),
    ])
    if docker_host:
        environment["DOCKER_HOST"] = docker_host
    return environment


def launch_runner(command: list[str], environment: dict, log_path: Path):
    """Stop the owned runner before cleaning up its remote sandboxes."""
    with log_path.open("w") as log:
        process = subprocess.Popen(command, env=environment, stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            code = process.wait()
            if code:
                raise RuntimeError(f"DeepSWE runner failed (exit {code}); see {log_path}")
        except BaseException:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            raise


def export_results(run_dir: Path, task_ids: list[str], model_name: str, run_id: str) -> Path:
    provenance = json.loads((run_dir / "run-config.json").read_text())
    evaluation = {
        "runtime_kind": provenance["runtime_kind"],
        "network_isolation": "docker-network-none" if provenance["runtime_kind"] == "docker" else "platform-managed-unverified",
        "dataset_revision": provenance.get("dataset_revision"),
        "network_isolation_required": provenance.get("require_network_isolation", False),
    }
    entries = json.loads((run_dir / "pier-results.json").read_text())
    by_id = {entry["task_id"]: entry for entry in entries}
    if set(by_id) != set(task_ids) or len(entries) != len(task_ids):
        raise ValueError("Pier results do not match the selected DeepSWE tasks")
    tasks, scores, failures = [], {}, {}
    for task_id in task_ids:
        entry = by_id[task_id]
        result = entry.get("result") or {}
        exception = result.get("exception_info")
        rewards = (result.get("verifier_result") or {}).get("rewards") or {}
        error = entry.get("error")
        stage = entry.get("stage", "execution")
        if exception:
            error = f"{exception['exception_type']}: {exception['exception_message']}"
        score = rewards.get("reward")
        trial_dir = run_dir / "trials" / task_id
        document = None
        try:
            document = load_validated_trajectory(trial_dir, model_name=model_name, run_id=run_id)
        except (OSError, ValueError, TypeError, KeyError, AttributeError, RuntimeError) as exc:
            # Match Mini's contract: an invalid trace is an unscored task.
            # Preserve the upstream error if execution already failed.
            if not error:
                error = f"{type(exc).__name__}: {exc}"
                stage = "inference" if isinstance(exc, InferenceError) else "trajectory"
        if not error and (isinstance(score, bool) or not isinstance(score, (int, float))
                          or not math.isfinite(score) or score not in (0, 1)):
            error = f"Verifier did not produce a binary reward (received {score!r})"
            stage = "grading"
        benchmark = {
            "name": "DeepSWE 1.1", "task_id": task_id,
            "status": "failed" if error else "completed",
            "score": None if error else float(score),
            "resolved": None if error else score == 1,
        }
        if error:
            benchmark.update(stage=stage, error=error)
            failures[task_id] = {"stage": stage, "error": error}
        output = None
        if document is not None:
            document["final_metrics"]["extra"]["benchmark"] = benchmark
            resources = {
                phase: json.loads(path.read_text())
                for phase in ("agent", "verifier")
                if (path := trial_dir / f"resources-{phase}.json").is_file()
            }
            document["extra"]["evaluation"] = {**evaluation, "resources": resources}
            # Output I/O failures abort the batch, as in minisweBenchmark.
            output = write_atif(document, run_dir / (
                "trajectory.atif.json" if len(task_ids) == 1 else f"trajectories/{task_id}.atif.json"
            ))
        scores[task_id] = {key: benchmark[key] for key in ("status", "score", "resolved")}
        tasks.append({"task_id": task_id, "output_file_path": str(output) if output else None,
                      "score": benchmark["score"], "resolved": benchmark["resolved"]})
    scored = [value for value in scores.values() if value["status"] == "completed"]
    summary = {"total_tasks": len(tasks), "scored_tasks": len(scored), "failed_tasks": len(failures),
               "resolved_tasks": sum(value["resolved"] is True for value in scored),
               "mean_score": sum(value["score"] for value in scored) / len(scored) if scored else None}
    metadata = {"benchmark": "DeepSWE 1.1", "summary": summary, "failed_tasks": failures,
                **evaluation}
    (run_dir / "benchmark.json").write_text(json.dumps({**metadata, "tasks": scores}, indent=2) + "\n")
    manifest = {**metadata, "schema_version": "EvalBenchmarkManifest-v1", "trajectory_schema_version": "ATIF-v1.8",
                "session_id": run_id, "model_name": model_name, "tasks": tasks}
    path = run_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    if len(tasks) == 1 and tasks[0]["output_file_path"]:
        return Path(tasks[0]["output_file_path"])
    return path


def eval_deepswe_benchmark(
    inference_config: str = "", rollout_config: str = "",
    pyromind_api_key: str = "", output_dir: str = "",
) -> dict:
    config, rollout = json.loads(inference_config), json.loads(rollout_config)
    endpoint = config["endpoint"].strip().rstrip("/")
    url = urlsplit(endpoint)
    if url.scheme not in {"http", "https"} or not url.netloc or url.query or url.fragment or url.username:
        raise ValueError("endpoint must be an HTTP(S) API base URL without credentials, query or fragment")
    model_name = config["model_name"].strip()
    if not model_name:
        raise ValueError("model_name cannot be empty")
    tasks_dir = Path(os.environ.get("DEEPSWE_TASKS", "/workspace/datasets/deep-swe/tasks")).expanduser().resolve()
    selected = select_tasks(tasks_dir, rollout.get("num_tasks", 1), rollout.get("start_index", 0))
    python = runtime_python()
    trajectory_model()
    existing_host = os.environ.get("DEEPSWE_DOCKER_HOST")
    require_isolation = os.environ.get("DEEPSWE_REQUIRE_NETWORK_ISOLATION", "0") == "1"
    if require_isolation:
        if not existing_host:
            raise RuntimeError("Strict network isolation requires a standard Docker daemon via DEEPSWE_DOCKER_HOST; "
                               "PyroMind SDK 0.1.15 does not enforce task network isolation.")
        server = subprocess.run(["/usr/local/bin/docker", "version", "--format", "{{.Server.Version}}"],
                                env=runner_environment("", existing_host), capture_output=True, text=True, check=True)
        if "docker-rt" in server.stdout.lower():
            raise RuntimeError("Strict network isolation cannot use a docker-rt daemon")
    if not existing_host and not pyromind_api_key.strip():
        raise ValueError("pyromind_api_key is required to start docker-rt; CLI users must set PYROMIND_API_KEY")
    run_id = f"deepswe-{uuid4().hex}"
    run_dir = Path(output_dir).expanduser().resolve() / run_id
    run_dir.mkdir(parents=True)
    runtime_kind = "docker" if existing_host else "pyromind"
    revision = subprocess.run(["git", "-C", str(tasks_dir.parent), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=False)
    run_config = {
        "run_id": run_id, "run_dir": str(run_dir), "endpoint": endpoint,
        "model_name": model_name.removeprefix("openai/"), "runtime_kind": runtime_kind,
        "inference_workers": rollout["inference_workers"], "grading_workers": rollout["grading_workers"],
        "task_paths": [str(path) for path in selected],
        "agent_timeout_sec": None,
        "require_network_isolation": require_isolation,
        "dataset_revision": revision.stdout.strip() if revision.returncode == 0 else None,
    }
    config_path = run_dir / "run-config.json"
    config_path.write_text(json.dumps(run_config, indent=2) + "\n")
    environment = runner_environment(config.get("api_key", ""))
    command = [str(python), str(SCRIPTS / "run_deepswe.py"), "--config", str(config_path)]
    subprocess.run([*command, "--check"], env=environment, check=True)
    owned_host = None
    try:
        docker_host = existing_host
        if not docker_host:
            owned_host = prepare_docker_context(pyromind_api_key, "us-west-1#pre", str(run_dir / "docker-rt.log"))
            docker_host = owned_host
        environment = runner_environment(config.get("api_key", ""), docker_host)
        launch_runner(command, environment, run_dir / "pier.log")
        output = export_results(run_dir, [p.name for p in selected], model_name, run_id)
        return {"output_file_path": str(output)}
    finally:
        if owned_host:
            stop_docker_context(owned_host, str(run_dir / "docker-rt.log"))
        elif existing_host:
            _remove_sandbox_containers(existing_host, run_dir)


if __name__ == "__main__":
    import argparse
    import tempfile

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint")
    parser.add_argument("--model-name")
    parser.add_argument("--num-tasks", type=int, default=1)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--inference-workers", type=int, default=1)
    parser.add_argument("--grading-workers", type=int, default=1)
    parser.add_argument("--output-dir", default="/workspace/eval_results")
    parser.add_argument("--check", action="store_true", help="Check task selection and dependencies only")
    args = parser.parse_args()
    if args.check:
        tasks_dir = Path(os.environ.get("DEEPSWE_TASKS", "/workspace/datasets/deep-swe/tasks"))
        paths = select_tasks(tasks_dir, args.num_tasks, args.start_index)
        with tempfile.TemporaryDirectory(prefix="deepswe-check-") as directory:
            config_path = Path(directory) / "check.json"
            config_path.write_text(json.dumps({"task_paths": [str(p.resolve()) for p in paths]}))
            subprocess.run([str(runtime_python()), str(SCRIPTS / "run_deepswe.py"),
                            "--config", str(config_path), "--check"], env=runner_environment(""), check=True)
    else:
        if not args.endpoint or not args.model_name:
            parser.error("--endpoint and --model-name are required unless using --check")
        result = eval_deepswe_benchmark(
            json.dumps({"endpoint": args.endpoint, "model_name": args.model_name,
                        "api_key": os.environ.get("OPENAI_API_KEY", "")}),
            json.dumps({"num_tasks": args.num_tasks, "start_index": args.start_index,
                        "inference_workers": args.inference_workers, "grading_workers": args.grading_workers}),
            os.environ.get("PYROMIND_API_KEY", ""), args.output_dir,
        )
        print(json.dumps(result))
