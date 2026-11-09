"""Grade each completed mini-swe-agent task in an independent worker pool."""

import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from pathlib import Path
from threading import Lock

from docker_ctx_prep import DOCKER_CLI_PATH, remove_task_sandboxes
from finish_evaluation import export_evaluation, load_trajectory, task_failure
from run_harness import grade_batch_predictions
from sandbox_tracking import write_agent_docker_launcher


def grade_task(
    task_id: str, prediction: dict, predictions_path: Path, run_dir: Path, *,
    model_name: str, run_id: str, docker_host: str,
) -> tuple[dict | None, dict]:
    document = None
    stage = "trajectory"
    try:
        document = load_trajectory(
            predictions_path, task_id, model_name=model_name, run_id=run_id,
        )
        stage = "grading"
        print(f"[{task_id}] grading started", flush=True)
        benchmarks = grade_batch_predictions(
            predictions_path, {task_id: prediction}, run_dir / "verified" / task_id,
            run_id=run_id, docker_host=docker_host, max_workers=1, tracking_dir=run_dir,
        )
        benchmark = benchmarks[task_id]
        print(f"[{task_id}] grading completed: score={benchmark['score']}", flush=True)
        return document, benchmark
    except Exception as exc:
        benchmark = task_failure(task_id, stage, exc)
        print(f"[{task_id}] {benchmark['stage']} failed: {benchmark['error']}", flush=True)
        return document, benchmark
    finally:
        remove_task_sandboxes(docker_host, run_dir, task_id)


def run_swebench(
    swebench_args: list[str], run_dir: Path, *, model_name: str, run_id: str,
    docker_host: str, grading_workers: int,
) -> Path:
    from minisweagent.run.benchmarks import swebench

    pending = {}
    benchmarks = {}
    lock = Lock()
    original = swebench.process_instance

    # mini-swe-agent owns the inference pool. Submit grading only after it has
    # saved the task's trajectory and prediction, without blocking that pool.
    with ThreadPoolExecutor(max_workers=grading_workers) as grading_pool:
        @wraps(original)
        def process_instance(instance, output_dir, config, progress_manager):
            task_id = instance["instance_id"]
            try:
                docker_launcher = write_agent_docker_launcher(
                    output_dir, run_id, DOCKER_CLI_PATH, task_id=task_id,
                )
                config = {
                    **config,
                    "environment": {**config["environment"], "executable": str(docker_launcher)},
                }
                original(instance, output_dir, config, progress_manager)
                predictions_path = output_dir / "preds.json"
                # mini-swe-agent rewrites this shared file under the same lock.
                with swebench._OUTPUT_FILE_LOCK:
                    prediction = json.loads(predictions_path.read_text(encoding="utf-8"))[task_id]
                future = grading_pool.submit(
                    grade_task, task_id, prediction, predictions_path, run_dir,
                    model_name=model_name, run_id=run_id, docker_host=docker_host,
                )
                with lock:
                    pending[task_id] = future
            except Exception as exc:
                # The upstream batch CLI logs worker exceptions and continues.
                # Keep the task in the summary even without a prediction file.
                with lock:
                    benchmarks[task_id] = task_failure(task_id, "inference", exc)
                remove_task_sandboxes(docker_host, run_dir, task_id)
                raise

        swebench.process_instance = process_instance
        try:
            swebench.app(swebench_args, standalone_mode=False)
        finally:
            swebench.process_instance = original
        # Leave the pool open until every inference callback has submitted work;
        # its context waits for all verifiers before the daemon can be cleaned up.

    if not pending and not benchmarks:
        raise ValueError("No SWE-bench tasks completed; check num_tasks and start_index")
    documents = {}
    for task_id, future in pending.items():
        document, benchmarks[task_id] = future.result()
        if document is not None:
            documents[task_id] = document
    return export_evaluation(
        documents, benchmarks, run_dir, model_name=model_name, run_id=run_id,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--grading-workers", type=int, required=True)
    parser.add_argument("swebench_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    run_swebench(
        args.swebench_args[1:], args.run_dir,
        model_name=args.model_name, run_id=args.run_id,
        docker_host=os.environ["DOCKER_HOST"], grading_workers=args.grading_workers,
    )


if __name__ == "__main__":
    main()
