"""Grade or reuse a report for saved predictions, then export ATIF-v1.8.

This entry point never calls model inference or starts docker-rt. To run a
verifier, supply an existing Docker host explicitly. Report replay is offline.
"""

import argparse
import json
from pathlib import Path
from uuid import uuid4

from atif_export import convert_to_atif, read_predictions, write_atif
from run_harness import grade_batch_predictions, read_grading_result


class InferenceError(RuntimeError):
    """mini-swe-agent saved an inference exception instead of a submission."""


def task_failure(task_id: str, stage: str, exc: Exception) -> dict:
    """Describe an unscored task without turning a runtime error into a zero."""
    return {
        "task_id": task_id, "status": "failed", "resolved": None, "score": None,
        "stage": "inference" if isinstance(exc, InferenceError) else stage,
        "error": f"{type(exc).__name__}: {exc}",
    }


def load_trajectory(
    predictions_path: Path, task_id: str, *, model_name: str, run_id: str,
) -> dict:
    native_path = predictions_path.parent / task_id / f"{task_id}.traj.json"
    native = json.loads(native_path.read_text(encoding="utf-8"))
    info = native["info"]
    if "exception_str" in info:
        raise InferenceError(f"{info['exit_status']}: {info['exception_str']}")
    document = convert_to_atif(
        native, task_id=task_id, model_name=model_name, session_id=run_id,
    )
    document["extra"]["native_trajectory_path"] = str(native_path.resolve())
    return document


def finish_evaluation(
    predictions_path: Path, output_dir: Path, *, model_name: str, run_id: str,
    docker_host: str | None = None, grading_dir: Path | None = None,
    grading_run_id: str | None = None,
    max_workers: int = 1,
) -> Path:
    if grading_dir is None and not docker_host:
        raise ValueError("Provide an existing grading directory or an explicit Docker host")
    if grading_dir is not None and (docker_host or not grading_run_id):
        raise ValueError("Report replay requires grading_run_id and no Docker host")
    predictions_path = predictions_path.resolve()
    output_dir = output_dir.resolve()
    predictions = read_predictions(predictions_path)
    # Convert and validate every trace once before starting the verifier.
    documents = {
        task_id: load_trajectory(
            predictions_path, task_id, model_name=model_name, run_id=run_id,
        )
        for task_id in predictions
    }
    if grading_dir is not None:
        benchmarks = {
            task_id: read_grading_result(
                grading_dir.resolve(), task_id,
                prediction["model_name_or_path"].replace("/", "__"), grading_run_id,
            )
            for task_id, prediction in predictions.items()
        }
    else:
        benchmarks = grade_batch_predictions(
            predictions_path, predictions, output_dir / "verified",
            run_id=run_id, docker_host=docker_host, max_workers=max_workers,
        )
    return export_evaluation(
        documents, benchmarks, output_dir, model_name=model_name, run_id=run_id,
    )


def export_evaluation(
    documents: dict[str, dict], benchmarks: dict[str, dict], output_dir: Path, *,
    model_name: str, run_id: str,
) -> Path:
    """Export available trajectories and list unscored tasks separately."""
    output_dir.mkdir(parents=True, exist_ok=True)
    benchmarks = dict(sorted(benchmarks.items()))
    tasks = []
    single_task = len(benchmarks) == 1
    for task_id, benchmark in benchmarks.items():
        output = None
        if task_id in documents:
            target = (
                output_dir / "trajectory.atif.json"
                if single_task
                else output_dir / "trajectories" / f"{task_id}.atif.json"
            )
            document = documents[task_id]
            document["final_metrics"]["extra"]["benchmark"] = benchmark
            output = write_atif(document, target)
        tasks.append({
            "task_id": task_id,
            "output_file_path": str(output) if output is not None else None,
            "score": benchmark["score"],
            "resolved": benchmark["resolved"],
        })
    scored = [benchmark for benchmark in benchmarks.values() if benchmark["status"] == "completed"]
    failures = {
        task_id: {"stage": benchmark["stage"], "error": benchmark["error"]}
        for task_id, benchmark in benchmarks.items() if benchmark["status"] == "failed"
    }
    summary = {
        "total_tasks": len(tasks),
        "scored_tasks": len(scored),
        "failed_tasks": len(failures),
        "resolved_tasks": sum(task["resolved"] is True for task in tasks),
        "mean_score": sum(benchmark["score"] for benchmark in scored) / len(scored) if scored else None,
    }
    scores = {}
    for task_id, benchmark in benchmarks.items():
        scores[task_id] = {
            "status": benchmark["status"],
            "resolved": benchmark["resolved"],
            "score": benchmark["score"],
        }
    (output_dir / "benchmark.json").write_text(
        json.dumps(
            {"summary": summary, "tasks": scores, "failed_tasks": failures},
            ensure_ascii=False, indent=2, allow_nan=False,
        ) + "\n",
        encoding="utf-8",
    )
    if single_task and tasks[0]["output_file_path"] is not None:
        return Path(tasks[0]["output_file_path"])
    manifest = {
        "schema_version": "EvalBenchmarkManifest-v1", "trajectory_schema_version": "ATIF-v1.8",
        "session_id": run_id, "benchmark": "SWE-bench Verified", "model_name": model_name,
        "summary": summary, "tasks": tasks, "failed_tasks": failures,
    }
    output = output_dir / "manifest.json"
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--workers", type=int, default=1, help="Verifier concurrency for multiple tasks")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--grading-dir", type=Path, help="Replay existing harness reports offline")
    source.add_argument("--docker-host", help="Run only grading against this existing Docker host")
    parser.add_argument("--grading-run-id", help="Original harness run ID, required for report replay")
    args = parser.parse_args()
    run_id = f"eval-{uuid4().hex}"
    output = finish_evaluation(
        args.predictions, args.output_dir / run_id,
        model_name=args.model_name, run_id=run_id,
        docker_host=args.docker_host, grading_dir=args.grading_dir,
        grading_run_id=args.grading_run_id,
        max_workers=args.workers,
    )
    print(json.dumps({"output_file_path": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
