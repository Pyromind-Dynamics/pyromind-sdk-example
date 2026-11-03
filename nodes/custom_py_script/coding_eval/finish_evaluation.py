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
    prediction = exporter["read_single_prediction"](predictions_path)
    task_id = prediction["instance_id"]
    native_path = predictions_path.parent / task_id / f"{task_id}.traj.json"
    # Validate the complete trace before starting a costly verifier subprocess.
    native = json.loads(native_path.read_text(encoding="utf-8"))
    exporter["convert_to_atif"](
        native, task_id=task_id, model_name=model_name, session_id=run_id,
    )
    if grading_dir is not None:
        benchmark = grader["read_grading_result"](
            grading_dir.resolve(), task_id,
            prediction["model_name_or_path"].replace("/", "__"), grading_run_id,
        )
    else:
        benchmark = grader["grade_predictions"](
            predictions_path, prediction, output_dir / "verified",
            run_id=run_id, docker_host=docker_host,
        )
    output = exporter["export_atif"](
        predictions_path, output_dir / "trajectory.atif.json",
        model_name=model_name, session_id=run_id, benchmark=benchmark,
    )
    (output_dir / "benchmark.json").write_text(
        json.dumps(benchmark, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-name", required=True)
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
    )
    print(json.dumps({"output_file_path": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
