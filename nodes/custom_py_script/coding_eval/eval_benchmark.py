"""Run selected SWE-bench tasks and return ATIF-v1.8 files or their manifest."""

import json
import os
import runpy
import subprocess
from importlib import import_module
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from uuid import uuid4


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


def resolve_model_name(endpoint: str, model_name: str | None, api_key: str | None = "") -> str:
    """Read served IDs without inference and resolve only unambiguous aliases."""
    requested = (model_name or "").strip()
    headers = {"Accept": "application/json"}
    service_key = (api_key or "").strip()
    if service_key:
        headers["Authorization"] = f"Bearer {service_key}"
    request = Request(
        f"{_api_base(endpoint)}/models",
        headers=headers,
    )
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(
            f"Model service /v1/models returned HTTP {exc.code}; "
            "check the endpoint and model service API key before starting evaluation."
        ) from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(
            "Cannot read model service /v1/models; check that the service is ready "
            "and reachable from the evaluation Pod."
        ) from exc
    except (ValueError, UnicodeError) as exc:
        raise ValueError("Model service /v1/models did not return valid JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ValueError("Model service /v1/models must return a data array")
    ids = sorted({
        item["id"] for item in payload["data"]
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]
    })
    available = ", ".join(repr(value) for value in ids) or "(none)"
    if not requested:
        if len(ids) == 1:
            print(f"Discovered served model ID {ids[0]!r}", flush=True)
            return ids[0]
        raise ValueError(
            "model_name may be omitted only when /v1/models returns exactly one model. "
            f"Available model IDs: {available}. Fill model_name to choose a model."
        )
    if requested in ids:
        return requested
    # A short directory/model name is a common UI input. Never override an
    # explicitly supplied full ID or select an unrelated sole available model.
    matches = [value for value in ids if value.rstrip("/").rsplit("/", 1)[-1] == requested]
    if "/" not in requested and len(matches) == 1:
        resolved = matches[0]
        print(f"Resolved model_name {requested!r} to served ID {resolved!r}", flush=True)
        return resolved
    raise ValueError(
        f"model_name {requested!r} is not an exact or unambiguous served ID. "
        f"Available model IDs: {available}. Use the exact data[].id from /v1/models."
    )


def launch_mini_extra_swebench(
    endpoint: str,
    model_name: str,
    api_key: str | None,
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
    # OpenAI-compatible clients require a nonempty key even for unprotected
    # local servers. Override inherited credentials with an inert placeholder.
    environment["OPENAI_API_KEY"] = (api_key or "").strip() or "dummy"
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
    model_name: str = "",
    api_key: str = "",
    pyromind_api_key: str = "",
    cluster: str = "",
    num_of_sandbox: int = 1,
    output_dir: str = "",
    num_tasks: int = 1,
    start_index: int = 0,
) -> dict:
    """Keep the prediction launcher, then grade and export the actual trace."""
    if not output_dir.strip():
        raise ValueError("output_dir must not be empty")
    _task_slice(num_tasks, start_index)
    _api_base(endpoint)
    for name, value in (("pyromind_api_key", pyromind_api_key), ("cluster", cluster)):
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
    check_model_dependencies()
    model_name = resolve_model_name(endpoint, model_name, api_key)
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
