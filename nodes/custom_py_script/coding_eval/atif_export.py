"""Export Mini SWE Agent's saved chat trajectory as a validated ATIF-v1.8 file.

No model, Docker, or evaluator is invoked by this module. The optional CLI can
convert existing artifacts independently of the workflow node.
"""

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def trajectory_model():
    """Load the reference validator before starting expensive node work."""
    try:
        from harbor.models.trajectories.trajectory import Trajectory
    except ImportError as exc:
        raise RuntimeError(
            "ATIF validation requires Harbor; install coding_eval/requirements.txt "
            "in the node's Python 3.12+ environment."
        ) from exc
    # Older Harbor models may import successfully but reject v1.8 later.
    versions = Trajectory.model_fields["schema_version"].annotation.__args__
    if "ATIF-v1.8" not in versions:
        raise RuntimeError("Installed Harbor does not support ATIF-v1.8")
    return Trajectory


def read_predictions(predictions_path: Path) -> dict[str, dict]:
    predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    return dict(sorted(predictions.items()))


def read_single_prediction(predictions_path: Path) -> dict:
    predictions = read_predictions(predictions_path)
    if len(predictions) != 1:
        raise ValueError("Select a task_id when exporting a multi-task prediction file")
    return next(iter(predictions.values()))


def _content(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list) and all(
        isinstance(part, dict) and part.get("type") == "text"
        and isinstance(part.get("text"), str) for part in value
    ):
        return [{"type": "text", "text": part["text"]} for part in value]
    raise ValueError("Unsupported native content; refusing to discard non-text data")


def _timestamp(message: dict) -> str | None:
    value = message.get("timestamp", (message.get("extra") or {}).get("timestamp"))
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat()
    raise ValueError("Invalid native message timestamp")


def _metrics(message: dict) -> dict:
    extra = message.get("extra") or {}
    response = extra.get("response") or {}
    usage = (response.get("usage") or {}) if isinstance(response, dict) else {}
    metrics = {}
    for key in ("prompt_tokens", "completion_tokens"):
        if key in usage and usage[key] is not None:
            value = usage[key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"Invalid native {key}")
            metrics[key] = value
    details = usage.get("prompt_tokens_details") or {}
    cached = details.get("cached_tokens")
    if cached is not None:
        if isinstance(cached, bool) or not isinstance(cached, int) or cached < 0:
            raise ValueError("Invalid native cached_tokens")
        metrics["cached_tokens"] = cached
    # mini-extra's ignore_errors cost mode uses zero for unavailable prices.
    cost = extra.get("cost")
    if isinstance(cost, (int, float)) and not isinstance(cost, bool) and math.isfinite(cost) and cost > 0:
        metrics["cost_usd"] = cost
    return metrics


def _steps_from_messages(messages: list) -> list[dict]:
    """Build steps and attach each tool observation to its agent call."""
    steps = []
    call_owners = {}
    for index, message in enumerate(messages):
        role = message.get("role")
        extra = message.get("extra") or {}
        content = _content(message.get("content"))
        timestamp = _timestamp(message)
        is_feedback = role == "tool" or (
            role == "user" and ("returncode" in extra or "interrupt_type" in extra)
        )
        if is_feedback:
            call_id = message.get("tool_call_id")
            if call_id:
                owner = call_owners.get(call_id)
            else:
                owner = steps[-1] if steps else None
            if owner is None or owner["source"] != "agent":
                raise ValueError(f"Native observation at index {index} has no matching agent call")
            result = {"content": content}
            if call_id:
                result["source_call_id"] = call_id
            metadata = {key: extra[key] for key in ("returncode", "exception_info") if key in extra}
            if timestamp:
                metadata["timestamp"] = timestamp
            if metadata:
                result["extra"] = metadata
            owner.setdefault("observation", {"results": []})["results"].append(result)
            continue
        step = {
            "step_id": len(steps) + 1,
            "source": {"assistant": "agent", "exit": "system"}.get(role, role),
            "message": content,
        }
        if timestamp:
            step["timestamp"] = timestamp
        if role == "exit":
            step["extra"] = {"native_role": "exit"}
            if extra.get("exit_status"):
                step["extra"]["exit_status"] = extra["exit_status"]
        if role == "assistant":
            step["llm_call_count"] = 1
            metrics = _metrics(message)
            if metrics:
                step["metrics"] = metrics
            if message.get("reasoning_content") is not None:
                step["reasoning_content"] = message["reasoning_content"]
            for call in message.get("tool_calls") or []:
                function = call["function"]
                arguments = function["arguments"]
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                call_id = call.get("id")
                if not isinstance(call_id, str) or not call_id or call_id in call_owners:
                    raise ValueError("Native tool call IDs must be nonempty and unique")
                step.setdefault("tool_calls", []).append({
                    "tool_call_id": call_id,
                    "function_name": function["name"], "arguments": arguments,
                })
                call_owners[call_id] = step
        steps.append(step)
    return steps


def convert_to_atif(
    native: dict, *, task_id: str, model_name: str, session_id: str,
    benchmark: dict | None = None,
) -> dict:
    """Convert saved chat-completions messages without synthesizing events."""
    if native.get("trajectory_format") != "mini-swe-agent-1.1":
        raise ValueError("Unsupported native trajectory format")
    if native.get("instance_id") != task_id:
        raise ValueError("Native trajectory and prediction task IDs must match")
    messages = native.get("messages")
    info = native.get("info") or {}
    version = info.get("mini_version")
    if benchmark is not None and benchmark.get("task_id") != task_id:
        raise ValueError("Grading result and trajectory task IDs must match")
    steps = _steps_from_messages(messages)
    agents = [step for step in steps if step["source"] == "agent"]
    if not agents:
        raise ValueError(
            f"Task {task_id} produced no model responses "
            f"(agent exit_status={info.get('exit_status', 'unknown')}). "
            "Check info.exception_str in the native trajectory for the upstream failure; "
            "grading and ATIF export cannot continue."
        )
    if not any(step["source"] == "user" for step in steps):
        raise ValueError("A task trajectory must contain user and agent messages")
    final_metrics = {
        "total_steps": len(steps),
        "extra": {
            "benchmark": benchmark or {
                "name": "SWE-bench Verified", "task_id": task_id, "status": "not_run",
            },
            "exit_status": info.get("exit_status"),
        },
    }
    for key in ("prompt_tokens", "completion_tokens", "cached_tokens", "cost_usd"):
        # An incomplete sum must not masquerade as the run's total usage.
        if all(key in step.get("metrics", {}) for step in agents):
            final_metrics[f"total_{key}"] = sum(step["metrics"][key] for step in agents)
    document = {
        "schema_version": "ATIF-v1.8", "session_id": session_id,
        "trajectory_id": f"{session_id}:{task_id}",
        "agent": {"name": "mini-swe-agent", "version": version, "model_name": model_name},
        "steps": steps, "final_metrics": final_metrics,
        "extra": {"original_format": native["trajectory_format"]},
    }
    return trajectory_model().model_validate(document).to_json_dict()


def export_atif(
    predictions_path: Path, output_path: Path, *, model_name: str,
    session_id: str, benchmark: dict | None = None,
    task_id: str | None = None,
) -> Path:
    if task_id is None:
        prediction = read_single_prediction(predictions_path)
    else:
        predictions = read_predictions(predictions_path)
        if task_id not in predictions:
            raise ValueError("Selected task_id is not in the prediction file")
        prediction = predictions[task_id]
    return export_prediction_atif(
        prediction, predictions_path.parent, output_path,
        model_name=model_name, session_id=session_id, benchmark=benchmark,
    )


def export_prediction_atif(
    prediction: dict, runs_dir: Path, output_path: Path, *, model_name: str,
    session_id: str, benchmark: dict | None = None,
) -> Path:
    """Export a prediction already validated by read_predictions.

    Batch callers reuse that parsed collection rather than re-reading every
    task's patch for each individual trajectory.
    """
    task_id = prediction["instance_id"]
    native_path = runs_dir / task_id / f"{task_id}.traj.json"
    if not native_path.is_file():
        raise FileNotFoundError(f"Original interaction trajectory is required: {native_path}")
    native = json.loads(native_path.read_text(encoding="utf-8"))
    document = convert_to_atif(
        native, task_id=task_id, model_name=model_name,
        session_id=session_id, benchmark=benchmark,
    )
    document["extra"]["native_trajectory_path"] = str(native_path.resolve())
    return write_atif(document, output_path)


def write_atif(document: dict, output_path: Path) -> Path:
    """Atomically write an already validated ATIF document."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_name(f".{output_path.name}.{uuid4().hex}.tmp")
    try:
        temporary_path.write_text(
            json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)
    return output_path.resolve()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--task-id", help="Select one task from a multi-task prediction file")
    parser.add_argument("--grading-report", type=Path, help="Existing normalized benchmark result JSON")
    args = parser.parse_args()
    benchmark = json.loads(args.grading_report.read_text(encoding="utf-8")) if args.grading_report else None
    if benchmark and args.task_id and "tasks" in benchmark:
        benchmark = benchmark["tasks"][args.task_id]
    print(export_atif(
        args.predictions.resolve(), args.output.resolve(), model_name=args.model_name,
        session_id=uuid4().hex, benchmark=benchmark, task_id=args.task_id,
    ))
