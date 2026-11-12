"""Validate Mini's saved trajectory before DeepSWE verification starts."""

import json
from pathlib import Path

from atif_export import convert_to_atif, trajectory_model


VALIDATED_TRACE = "trajectory.atif.json"


class InferenceError(RuntimeError):
    """Mini saved a model/agent exception instead of a valid submission."""


def load_trajectory(trial_dir: Path, *, model_name: str, run_id: str) -> dict:
    task_id = trial_dir.name
    native_path = trial_dir / "agent/mini-swe-agent.trajectory.json"
    native = json.loads(native_path.read_text())
    info = native.get("info") or {}
    if "exception_str" in info:
        raise InferenceError(f"Agent inference failed: {info.get('exit_status')}: {info['exception_str']}")
    document = convert_to_atif(
        native, task_id=task_id, model_name=model_name, session_id=run_id,
        benchmark={"name": "DeepSWE 1.1", "task_id": task_id, "status": "not_run"},
    )
    document["extra"].update(native_trajectory_path=str(native_path), benchmark="DeepSWE 1.1")
    return document


def load_validated_trajectory(trial_dir: Path, *, model_name: str, run_id: str) -> dict:
    """Reuse pre-grading conversion; allow offline export of older runs."""
    path = trial_dir / "agent" / VALIDATED_TRACE
    if not path.is_file():
        return load_trajectory(trial_dir, model_name=model_name, run_id=run_id)
    document = trajectory_model().model_validate_json(path.read_text()).to_json_dict()
    if document["session_id"] != run_id or document["trajectory_id"] != f"{run_id}:{trial_dir.name}":
        raise ValueError("Validated trajectory does not match this run and task")
    return document
