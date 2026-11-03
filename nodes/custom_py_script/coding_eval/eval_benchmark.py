"""Run selected SWE-bench tasks and return ATIF-v1.8 files or their manifest."""

import json
import os
import runpy
import subprocess
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4


def _task_slice(num_tasks: int, start_index: int) -> str:
    if isinstance(num_tasks, bool) or not isinstance(num_tasks, int) or num_tasks < 1:
        raise ValueError("num_tasks must be a positive integer")
    if isinstance(start_index, bool) or not isinstance(start_index, int) or start_index < 0:
        raise ValueError("start_index must be a nonnegative integer")
    return f"{start_index}:{start_index + num_tasks}"


def _api_base(endpoint: str) -> str:
    endpoint = endpoint.strip().rstrip("/")
    parsed = urlsplit(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("endpoint must be an HTTP(S) URL")
    if parsed.query or parsed.fragment or parsed.path not in {"", "/v1"}:
        raise ValueError("endpoint must be a server URL or an OpenAI API base ending in /v1")
    return endpoint if parsed.path == "/v1" else f"{endpoint}/v1"


def launch_mini_extra_swebench(
    endpoint: str,
    model_name: str,
    api_key: str,
    num_of_sandbox: int,
    output_dir: str,
    *,
    docker_host: str | None = None,
    num_tasks: int = 1,
    start_index: int = 0,
) -> Path:
    """Run selected SWE-bench Verified tasks and return the native preds.json.

    num_of_sandbox controls concurrent mini-extra workers. The supplied endpoint
    must be reachable from the benchmark containers as well as from this process.
    """
    slice_spec = _task_slice(num_tasks, start_index)
    if isinstance(num_of_sandbox, bool) or not isinstance(num_of_sandbox, int) or num_of_sandbox < 1:
        raise ValueError("num_of_sandbox must be a positive integer")
    if not output_dir.strip():
        raise ValueError("output_dir must not be empty")
    if not model_name.strip():
        raise ValueError("model_name must not be empty")
    if not api_key.strip():
        raise ValueError("api_key must not be empty")

    api_base = _api_base(endpoint)
    litellm_model = f"openai/{model_name.strip()}"
    runs_dir = Path(output_dir).expanduser().resolve()
    runs_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "mini-extra",
        "swebench",
        "-c", "swebench.yaml",
        "-c", f"model.model_name={json.dumps(litellm_model)}",
        "-c", "model.cost_tracking=ignore_errors",
        "-c", "model.model_kwargs.custom_llm_provider=openai",
        "-c", f"model.model_kwargs.api_base={json.dumps(api_base)}",
        "-c", "model.model_kwargs.drop_params=true",
        "-c", "model.model_kwargs.timeout=300",
        "-c", "agent.cost_limit=9999",
        "-c", "agent.wall_time_limit_seconds=7000",
        "-c", "agent.step_limit=150",
        "-c", "environment.pull_timeout=7200",
        "--subset", "verified",
        "--split", "test",
        "--slice", slice_spec,
        "-w", str(num_of_sandbox),
        "-o", str(runs_dir),
    ]

    environment = os.environ.copy()
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
    endpoint: str,
    model_name: str,
    api_key: str,
    pyromind_api_key: str,
    cluster: str,
    num_of_sandbox: int,
    output_dir: str,
    num_tasks: int = 1,
    start_index: int = 0,
) -> dict:
    """Keep the prediction launcher, then grade and export the actual trace."""
    if not output_dir.strip():
        raise ValueError("output_dir must not be empty")
    _task_slice(num_tasks, start_index)
    _api_base(endpoint)
    for name, value in (("model_name", model_name), ("api_key", api_key),
                        ("pyromind_api_key", pyromind_api_key), ("cluster", cluster)):
        if not value.strip():
            raise ValueError(f"{name} must not be empty")
    if isinstance(num_of_sandbox, bool) or not isinstance(num_of_sandbox, int) or num_of_sandbox < 1:
        raise ValueError("num_of_sandbox must be a positive integer")
    # Load helpers by file path, like docker-ctx-prep.py, so Pod loaders do not
    # need this directory on sys.path or installed as a Python package.
    script_dir = Path(__file__).parent
    exporter = runpy.run_path(str(script_dir / "atif_export.py"))
    finisher = runpy.run_path(str(script_dir / "finish_evaluation.py"))
    exporter["trajectory_model"]()
    run_id = f"eval-{uuid4().hex}"
    run_dir = Path(output_dir).expanduser().resolve() / run_id
    run_dir.mkdir(parents=True)
    runs_dir = run_dir / "runs"
    docker_context = runpy.run_path(
        str(Path(__file__).with_name("docker-ctx-prep.py"))
    )
    docker_host = docker_context["prepare_docker_context"](
        pyromind_api_key, cluster, str(run_dir / "docker-rt.log")
    )
    print("docker-rt launched")

    try:
        predictions = launch_mini_extra_swebench(
            endpoint, model_name, api_key, num_of_sandbox, str(runs_dir),
            docker_host=docker_host,
            num_tasks=num_tasks, start_index=start_index,
        )
        output_path = finisher["finish_evaluation"](
            predictions, run_dir, model_name=model_name, run_id=run_id,
            docker_host=docker_host,
            max_workers=num_of_sandbox,
        )
        return {"output_file_path": str(output_path)}
    finally:
        docker_context["stop_docker_context"](docker_host, str(run_dir / "docker-rt.log"))
