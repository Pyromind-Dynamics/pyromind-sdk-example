"""Launch the SWE-bench agent against an existing OpenAI-compatible endpoint.

This module runs the prediction phase only. Grading and ATIF export are pending.
"""

import json
import os
import runpy
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


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
) -> Path:
    """Run one SWE-bench Verified task and return the native preds.json path.

    num_of_sandbox controls concurrent mini-extra workers. The supplied endpoint
    must be reachable from the benchmark containers as well as from this process.
    """
    if isinstance(num_of_sandbox, bool) or num_of_sandbox < 1:
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
        "--slice", "0:1",
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
) -> dict:
    """Run one SWE-bench Verified task and return the native prediction file path.

    Grading and ATIF export remain to be implemented.
    """
    if not output_dir.strip():
        raise ValueError("output_dir must not be empty")
    runs_dir = Path(output_dir).expanduser().resolve()
    prepare_docker_context = runpy.run_path(
        str(Path(__file__).with_name("docker-ctx-prep.py"))
    )["prepare_docker_context"]
    docker_host = prepare_docker_context(
        pyromind_api_key, cluster, str(runs_dir / "docker-rt.log")
    )
    print("docker-rt launched")

    predictions = launch_mini_extra_swebench(
        endpoint, model_name, api_key, num_of_sandbox, output_dir,
        docker_host=docker_host,
    )
    return {"output_file_path": str(predictions)}
