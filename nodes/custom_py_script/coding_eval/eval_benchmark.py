"""Run selected SWE-bench tasks and return ATIF-v1.8 files or their manifest."""

import json
import os
import subprocess
import sys
from importlib import import_module
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

from atif_export import trajectory_model
from docker_ctx_prep import prepare_docker_context, stop_docker_context
from finish_evaluation import finish_evaluation


def check_model_dependencies() -> None:
    """Validate the tool-calling import path before creating a remote sandbox."""
    try:
        import_module("litellm.responses.mcp.chat_completions_handler")
    except ImportError as exc:
        raise RuntimeError(
            "Model tool-calling dependencies are incomplete. Install "
            "coding_eval/requirements.txt in this interpreter "
            "(requires litellm[mcp]==1.106.6) before starting evaluation."
        ) from exc


def _task_slice(num_tasks: int, start_index: int) -> str:
    if num_tasks < 1:
        raise ValueError("num_tasks must be a positive integer")
    if start_index < 0:
        raise ValueError("start_index must be a nonnegative integer")
    return f"{start_index}:{start_index + num_tasks}"


def launch_mini_extra_swebench(
    endpoint: str,
    model_name: str,
    api_key: str,
    works: int,
    output_dir: str,
    *,
    docker_host: str | None = None,
    slice_spec: str = "0:1",
) -> Path:
    """Run selected SWE-bench Verified tasks and return the native preds.json.

    slice_spec is prepared by the node entry point. works controls
    concurrent mini-extra workers. The supplied endpoint
    must be reachable from the benchmark containers as well as from this process.
    """
    litellm_model = f"openai/{model_name}"
    runs_dir = Path(output_dir).expanduser().resolve()
    runs_dir.mkdir(parents=True, exist_ok=True)

    command = [
        sys.executable, "-m", "minisweagent.run.utilities.mini_extra",
        "swebench",
        "-c", "swebench.yaml",
        "-c", f"model.model_name={json.dumps(litellm_model)}",
        "-c", "model.cost_tracking=ignore_errors",
        "-c", "model.model_kwargs.custom_llm_provider=openai",
        "-c", f"model.model_kwargs.api_base={json.dumps(endpoint)}",
        "-c", "model.model_kwargs.drop_params=true",
        "-c", "model.model_kwargs.timeout=300",
        "-c", "agent.cost_limit=9999",
        "-c", "agent.wall_time_limit_seconds=7000",
        "-c", "agent.step_limit=150",
        "-c", "environment.pull_timeout=7200",
        "--subset", "verified",
        "--split", "test",
        "--slice", slice_spec,
        "-w", str(works),
        "-o", str(runs_dir),
    ]

    environment = os.environ.copy()
    # Use the supplied model-service key instead of an inherited credential.
    environment["OPENAI_API_KEY"] = api_key.strip()
    if docker_host:
        environment["DOCKER_HOST"] = docker_host
    environment["TTY_COMPATIBLE"] = "0"
    environment.pop("FORCE_COLOR", None)
    subprocess.run(command, env=environment, check=True)

    predictions = runs_dir / "preds.json"
    if not predictions.is_file():
        raise FileNotFoundError(f"mini-extra finished without {predictions}")
    return predictions


def eval_benchmark(
    inference_config: str = "",
    rollout_config: str = "",
    pyromind_api_key: str = "",
    output_dir: str = "",
) -> dict:
    """Keep the prediction launcher, then grade and export the actual trace."""
    rollout = json.loads(rollout_config)
    works = rollout["works"]
    slice_spec = _task_slice(rollout["num_tasks"], rollout["start_index"])
    config = json.loads(inference_config)
    endpoint = config["endpoint"].strip().rstrip("/")
    parsed = urlsplit(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError("endpoint must be an HTTP(S) API base URL without query parameters or fragments")
    model_name = config["model_name"].strip()
    api_key = config["api_key"]
    trajectory_model()
    check_model_dependencies()
    run_id = f"eval-{uuid4().hex}"
    run_dir = Path(output_dir).expanduser().resolve() / run_id
    run_dir.mkdir(parents=True)
    runs_dir = run_dir / "runs"
    docker_host = prepare_docker_context(
        pyromind_api_key, "us-west-1#pre", str(run_dir / "docker-rt.log")
    )
    print("docker-rt launched")

    try:
        predictions = launch_mini_extra_swebench(
            endpoint, model_name, api_key, works, str(runs_dir),
            docker_host=docker_host,
            slice_spec=slice_spec,
        )
        output_path = finish_evaluation(
            predictions, run_dir, model_name=model_name, run_id=run_id,
            docker_host=docker_host,
            max_workers=works,
        )
        return {"output_file_path": str(output_path)}
    finally:
        stop_docker_context(docker_host, str(run_dir / "docker-rt.log"))
