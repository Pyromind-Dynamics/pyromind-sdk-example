"""Grade an existing single-task prediction; never perform model inference.

Based on PyroDash/evaluation/evaluation_code/swe-bench/run_harness.py's
SWE-bench 5.x invocation and extended Docker API timeout.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


DATASET_NAME = "SWE-bench/SWE-bench_Verified"


def grade_predictions(
    predictions_path: Path, prediction: dict, output_dir: Path, *,
    run_id: str, docker_host: str,
) -> dict:
    """Run the verifier and distinguish an unresolved task from a harness error."""
    output_dir.mkdir(parents=True, exist_ok=True)
    task_id = prediction["instance_id"]
    model_directory = prediction["model_name_or_path"].replace("/", "__")
    if model_directory in {".", ".."} or "\\" in model_directory:
        raise ValueError("Invalid prediction model name")
    runner = Path(os.environ.get("PYROMIND_HARNESS_RUNNER", __file__)).resolve()
    if not runner.is_file():
        raise FileNotFoundError(f"Harness runner not found: {runner}")
    command = [
        os.environ.get("HARNESS_PYTHON", sys.executable), str(runner),
        "--dataset_name", DATASET_NAME,
        "--predictions_path", str(predictions_path.resolve()),
        "--instance_ids", task_id,
        "--max_workers", "1", "--run_id", run_id,
        "--report_dir", str(output_dir.resolve()),
    ]
    environment = os.environ.copy()
    environment["DOCKER_HOST"] = docker_host
    log_path = output_dir / "harness.log"
    with log_path.open("w", encoding="utf-8") as log:
        try:
            subprocess.run(
                command, env=environment, cwd=output_dir, stdout=log,
                stderr=subprocess.STDOUT, check=True, timeout=14400,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError(f"SWE-bench harness failed; see {log_path}") from exc
    return read_grading_result(output_dir, task_id, model_directory, run_id)


def read_grading_result(output_dir: Path, task_id: str, model_directory: str, run_id: str) -> dict:
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
    import runpy

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
    sys.argv = ["swebench.harness.run_evaluation", *sys.argv[1:]]
    runpy.run_module("swebench.harness.run_evaluation", run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    main()
