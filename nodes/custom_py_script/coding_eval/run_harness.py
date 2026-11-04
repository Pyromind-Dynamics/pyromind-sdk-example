"""Grade existing predictions; never perform model inference.

Based on PyroDash/evaluation/evaluation_code/swe-bench/run_harness.py's
SWE-bench 5.x invocation and extended Docker API timeout.
"""

import json
import os
import runpy
import signal
import subprocess
import sys
import warnings
from functools import wraps
from inspect import signature
from pathlib import Path


DATASET_NAME = "SWE-bench/SWE-bench_Verified"


def configure_docker_rt_root_exec() -> None:
    """Avoid a redundant root switch when docker-rt's default identity is root.

    SDK 0.1.15 translates an explicit exec user into setpriv --init-groups,
    which can fail in a sandbox that already runs as root but cannot setgroups.
    Verify the actual default UID/GID before using it; never change privileges.
    This adapter is installed only in the verifier subprocess using docker-rt.
    """
    from docker.models.containers import Container

    original = Container.exec_run
    parameters = signature(original)

    @wraps(original)
    def exec_run(container, *args, **kwargs):
        bound = parameters.bind(container, *args, **kwargs)
        if bound.arguments.get("user") in {"root", "0", "root:root", "0:0"}:
            identity = original(container, ["/bin/sh", "-c", "id -u; id -g"])
            if identity.exit_code != 0 or identity.output.split() != [b"0", b"0"]:
                raise RuntimeError(
                    "docker-rt harness requires the sandbox's default UID and GID to be 0; "
                    "the current sandbox cannot use the root exec compatibility adapter."
                )
            bound.arguments["user"] = ""
        return original(*bound.args, **bound.kwargs)

    Container.exec_run = exec_run


def _safe_component(value: str) -> None:
    if not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError("Invalid harness artifact path component")


def check_docker_host(docker_host: str) -> None:
    """Fail before fetching datasets if the explicitly supplied daemon is absent."""
    import docker

    client = None
    try:
        client = docker.DockerClient(base_url=docker_host, timeout=5)
        if not client.ping():
            raise RuntimeError("Docker ping failed")
    except (docker.errors.DockerException, OSError, RuntimeError) as exc:
        raise RuntimeError("Docker host is unavailable; start or supply an existing daemon before grading") from exc
    finally:
        if client is not None:
            client.close()


def _terminate_process_group(process) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=10)
    except ProcessLookupError:
        process.wait(timeout=10)


def _cleanup_task_containers(docker_host: str, task_id: str | list[str], run_id: str, log_path: Path) -> None:
    """Best effort cleanup of this exact run's verifier containers, never prune."""
    client = None
    try:
        import docker

        client = docker.DockerClient(base_url=docker_host, timeout=10)
        task_ids = [task_id] if isinstance(task_id, str) else task_id
        prefixes = {f"sweb.eval.{value.lower()}.{run_id}" for value in task_ids}
        for row in client.api.containers(all=True):
            names = row.get("Names") or [row.get("name", "")]
            owned = any(
                name.lstrip("/") in prefixes
                or (name.lstrip("/").rsplit(".", 1)[0] in prefixes
                    and name.rsplit(".", 1)[-1].isdigit())
                for name in names
            )
            if owned:
                client.api.remove_container(row.get("Id") or row["id"], force=True)
    except Exception as exc:
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"Verifier container cleanup failed: {type(exc).__name__}\n")
        warnings.warn(f"Verifier cleanup incomplete; see {log_path}", RuntimeWarning)
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass


def grade_batch_predictions(
    predictions_path: Path, predictions: dict[str, dict], output_dir: Path, *,
    run_id: str, docker_host: str, max_workers: int = 1,
) -> dict[str, dict]:
    """Grade predictions validated by read_predictions in one verifier invocation."""
    if isinstance(max_workers, bool) or not isinstance(max_workers, int) or max_workers < 1:
        raise ValueError("max_workers must be a positive integer")
    output_dir.mkdir(parents=True, exist_ok=True)
    task_ids = sorted(predictions)
    model_directory = predictions[task_ids[0]]["model_name_or_path"].replace("/", "__")
    for value in (*task_ids, model_directory, run_id):
        _safe_component(value)
    check_docker_host(docker_host)
    runner = Path(os.environ.get("PYROMIND_HARNESS_RUNNER", __file__)).resolve()
    if not runner.is_file():
        raise FileNotFoundError(f"Harness runner not found: {runner}")
    command = [
        os.environ.get("HARNESS_PYTHON", sys.executable), str(runner),
        "--dataset_name", DATASET_NAME,
        "--predictions_path", str(predictions_path.resolve()),
        "--instance_ids", *task_ids,
        "--max_workers", str(min(max_workers, len(task_ids))), "--run_id", run_id,
        "--report_dir", str(output_dir.resolve()),
    ]
    environment = os.environ.copy()
    environment["DOCKER_HOST"] = docker_host
    log_path = output_dir / "harness.log"
    with log_path.open("w", encoding="utf-8") as log:
        with subprocess.Popen(
            command, env=environment, cwd=output_dir, stdout=log,
            stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True,
        ) as process:
            try:
                returncode = process.wait(timeout=14400)
            except BaseException as exc:
                _terminate_process_group(process)
                _cleanup_task_containers(docker_host, task_ids, run_id, output_dir / "cleanup.log")
                if isinstance(exc, subprocess.TimeoutExpired):
                    raise RuntimeError(f"SWE-bench harness timed out; see {log_path}") from exc
                raise
            if returncode:
                _cleanup_task_containers(docker_host, task_ids, run_id, output_dir / "cleanup.log")
                raise RuntimeError(f"SWE-bench harness failed; see {log_path}")
    return {
        task_id: read_grading_result(output_dir, task_id, model_directory, run_id)
        for task_id in task_ids
    }


def read_grading_result(output_dir: Path, task_id: str, model_directory: str, run_id: str) -> dict:
    for value in (task_id, model_directory, run_id):
        _safe_component(value)
    report_path = output_dir / f"{model_directory}.{run_id}.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if any(task_id in report.get(key, []) for key in (
        "error_ids", "incomplete_ids", "infra_failure_ids",
    )):
        raise RuntimeError(f"Harness did not complete task {task_id}; see {report_path}")
    resolved = task_id in report.get("resolved_ids", [])
    unresolved = task_id in report.get("unresolved_ids", [])
    empty = task_id in report.get("empty_patch_ids", [])
    if sum((resolved, unresolved, empty)) != 1:
        raise RuntimeError(f"Harness report has no unambiguous task result; see {report_path}")
    benchmark = {
        "name": "SWE-bench Verified", "dataset_name": DATASET_NAME,
        "task_id": task_id, "status": "completed",
        "resolved": resolved, "score": float(resolved),
        "report_file_path": str(report_path.resolve()),
    }
    if empty:
        benchmark["reason"] = "empty_patch"
    else:
        task_report_path = (
            output_dir / "logs" / "run_evaluation" / run_id
            / model_directory / task_id / "report.json"
        )
        if not task_report_path.is_file():
            # PyroDash's eval.sh flattens task reports after the verifier exits.
            task_report_path = output_dir / task_id / "report.json"
        task_report = json.loads(task_report_path.read_text(encoding="utf-8"))
        result = task_report.get(task_id)
        if not isinstance(result, dict) or result.get("resolved") is not resolved:
            raise ValueError("Harness summary and task report disagree")
        benchmark["task_report_file_path"] = str(task_report_path.resolve())
        benchmark["verifier_result"] = result
    return benchmark


def main() -> None:
    # Imported only by the harness subprocess. ATIF-only conversion and tests
    # do not need Docker, datasets, or a running daemon.
    import docker
    from docker.client import DockerClient

    original_from_env = docker.from_env
    original_client_from_env = DockerClient.from_env

    def from_env(*args, **kwargs):
        kwargs.setdefault("timeout", 300)
        return original_from_env(*args, **kwargs)

    @classmethod
    def client_from_env(cls, *args, **kwargs):
        kwargs.setdefault("timeout", 300)
        return original_client_from_env(*args, **kwargs)

    docker.from_env = from_env
    DockerClient.from_env = client_from_env
    client = docker.from_env()
    try:
        if client.version().get("GitCommit") == "docker-rt":
            configure_docker_rt_root_exec()
    finally:
        client.close()
    sys.argv = ["swebench.harness.run_evaluation", *sys.argv[1:]]
    runpy.run_module("swebench.harness.run_evaluation", run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    main()
