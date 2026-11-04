"""Grade or reuse a report for saved predictions, then export ATIF-v1.8.

This entry point never calls model inference or starts docker-rt. To run a
verifier, supply an existing Docker host explicitly. Report replay is offline.
"""

import argparse
import json
import runpy
from pathlib import Path
from uuid import uuid4


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
    scripts = Path(__file__).parent
    exporter = runpy.run_path(str(scripts / "atif_export.py"))
    grader = runpy.run_path(str(scripts / "run_harness.py"))
    predictions_path = predictions_path.resolve()
    output_dir = output_dir.resolve()
    predictions = exporter["read_predictions"](predictions_path)
    # Convert and validate every trace once before starting the verifier.
    documents = {}
    for task_id in predictions:
        native_path = predictions_path.parent / task_id / f"{task_id}.traj.json"
        native = json.loads(native_path.read_text(encoding="utf-8"))
        document = exporter["convert_to_atif"](
            native, task_id=task_id, model_name=model_name, session_id=run_id,
        )
        document["extra"]["native_trajectory_path"] = str(native_path.resolve())
        documents[task_id] = document
    if grading_dir is not None:
        benchmarks = {
            task_id: grader["read_grading_result"](
                grading_dir.resolve(), task_id,
                prediction["model_name_or_path"].replace("/", "__"), grading_run_id,
            )
            for task_id, prediction in predictions.items()
        }
    else:
        benchmarks = grader["grade_batch_predictions"](
            predictions_path, predictions, output_dir / "verified",
            run_id=run_id, docker_host=docker_host, max_workers=max_workers,
        )
    tasks = []
    single_task = len(predictions) == 1
    for task_id in predictions:
        benchmark = benchmarks[task_id]
        if benchmark.get("task_id") != task_id:
            raise ValueError("Grading result and trajectory task IDs must match")
        target = (output_dir / "trajectory.atif.json" if single_task else
                  output_dir / "trajectories" / f"{task_id}.atif.json")
        document = documents.pop(task_id)
        document["final_metrics"]["extra"]["benchmark"] = benchmark
        output = exporter["write_atif"](document, target)
        tasks.append({"task_id": task_id, "output_file_path": str(output),
                      "score": benchmark["score"], "resolved": benchmark.get("resolved")})
    summary = {
        "total_tasks": len(tasks),
        "resolved_tasks": sum(task["resolved"] is True for task in tasks),
        "mean_score": sum(task["score"] for task in tasks) / len(tasks),
    }
    (output_dir / "benchmark.json").write_text(
        json.dumps(benchmarks[tasks[0]["task_id"]] if single_task else
                   {"summary": summary, "tasks": benchmarks},
                   ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    if single_task:
        return output
    manifest = {
        "schema_version": "EvalBenchmarkManifest-v1", "trajectory_schema_version": "ATIF-v1.8",
        "session_id": run_id, "benchmark": "SWE-bench Verified", "model_name": model_name,
        "summary": summary, "tasks": tasks,
    }
    output = output_dir / "manifest.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
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
    if args.grading_dir is not None and not args.grading_run_id:
        parser.error("--grading-run-id is required with --grading-dir")
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
