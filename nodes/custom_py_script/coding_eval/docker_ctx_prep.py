"""Prepare a Docker CLI and start the PyroMind docker-rt daemon for SWE-bench."""

import os
import json
import re
import shutil
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

from sandbox_tracking import CONTAINER_RECORDS_DIR, container_belongs_to_run

DOCKER_CLI_URL = "https://download.docker.com/linux/static/stable/x86_64/docker-27.5.1.tgz"
DOCKER_CLI_PATH = Path("/usr/local/bin/docker")


def _install_docker_cli() -> None:
    """Install the requested Docker CLI version if the target has no CLI."""
    if DOCKER_CLI_PATH.is_file() and os.access(DOCKER_CLI_PATH, os.X_OK):
        return

    with tempfile.TemporaryDirectory(prefix="docker-cli-") as temporary_dir:
        archive = Path(temporary_dir) / "docker.tgz"
        subprocess.run(
            ["curl", "-fsSL", "--retry", "3", "--connect-timeout", "15",
             "--max-time", "300", "--output", str(archive), DOCKER_CLI_URL], check=True,
        )
        subprocess.run(
            ["tar", "-xzf", str(archive), "-C", temporary_dir, "docker/docker"], check=True
        )

        command = ["install", "-m", "755", str(Path(temporary_dir) / "docker/docker"), str(DOCKER_CLI_PATH)]
        if os.geteuid() != 0:
            command = ["sudo", "-n", *command]
        subprocess.run(command, check=True)


def prepare_docker_context(pyromind_api_key: str, cluster: str = "us-west-1#pre", log_file: str = "/workspace/docker-watch.log") -> str:
    """Start an owned daemon with a private socket and Docker config directory."""
    log_path = Path(log_file).expanduser().resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    capability = subprocess.run(
        [sys.executable, "-m", "pyromind_sdk.cli", "docker-rt", "--help"],
        capture_output=True, text=True, timeout=30, check=False,
    )
    if capability.returncode or "--sock" not in capability.stdout or "--pid-file" not in capability.stdout:
        raise RuntimeError("The node requires pyromind-sdk==0.1.15 with docker-rt socket/PID support")
    _install_docker_cli()

    # Unix-domain socket paths have a small length limit. A private /tmp
    # directory works even when output_dir is deeply nested on a shared volume.
    socket_dir = Path(tempfile.mkdtemp(prefix="pyromind-eval-"))
    socket_path = socket_dir / "docker.sock"
    pid_path = log_path.parent / "docker-rt.pid"
    config_path = log_path.parent / "docker-config"
    config_path.mkdir(mode=0o700, exist_ok=True)
    state = {"socket_dir": str(socket_dir), "socket": str(socket_path),
             "pid_file": str(pid_path), "docker_config": str(config_path), "status": "starting"}
    state_path = log_path.parent / "docker-rt-state.json"
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    environment = os.environ.copy()
    environment["PATH"] = f"{DOCKER_CLI_PATH.parent}{os.pathsep}{environment.get('PATH', '')}"
    environment["DOCKER_RT_SOCK"] = str(socket_path)
    environment["DOCKER_RT_PID_FILE"] = str(pid_path)
    environment["DOCKER_CONFIG"] = str(config_path)
    environment["PYROMIND_API_KEY"] = pyromind_api_key.strip()
    environment["PYROMIND_CLUSTER"] = cluster.strip()
    environment.pop("DOCKER_HOST", None)
    environment.pop("DOCKER_RT_HOST", None)
    environment["PYROMIND_DOCKER_RT_SKIP_WRAPPER_PROMPT"] = "1"
    command = [
        sys.executable, "-m", "pyromind_sdk.cli", "docker-rt", "--daemon",
        "--sock", str(socket_path), "--pid-file", str(pid_path),
        "--log-file", str(log_path),
    ]
    host = f"unix://{socket_path}"
    try:
        with log_path.open("a", encoding="utf-8") as log:
            result = subprocess.run(
                command, env=environment, check=False, timeout=180,
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
            )
        if result.returncode != 0:
            raise RuntimeError(f"docker-rt failed to start; see {log_path}")
        state["status"] = "started"
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        return host
    except BaseException:
        stop_docker_context(host, str(log_path))
        raise


def stop_docker_context(docker_host: str, log_file: str) -> None:
    """Remove this run's sandbox containers and stop its daemon."""
    run_dir = Path(log_file).expanduser().resolve().parent
    state_path = run_dir / "docker-rt-state.json"
    try:
        if not state_path.is_file():
            return
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if state.get("status") == "stopped":
            return
        if docker_host != f"unix://{state['socket']}":
            raise ValueError("Cleanup socket does not belong to this run")
        _remove_sandbox_containers(docker_host, run_dir)
        pid_file = Path(state["pid_file"])
        if pid_file.is_file():
            # A malformed/missing PID would make the SDK scan other processes.
            # Validate ownership and give it a stable private copy instead.
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            if pid <= 1:
                raise ValueError("Invalid owned daemon PID")
            if not _pid_uses_socket(pid, state["socket"]):
                pid_file.unlink(missing_ok=True)
            else:
                _stop_owned_pid(pid, state, run_dir)
                pid_file.unlink(missing_ok=True)
        elif Path(state["socket"]).exists():
            raise RuntimeError("Socket exists without an owned PID file; manual cleanup is required")
        shutil.rmtree(state["socket_dir"])
        state["status"] = "stopped"
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    except Exception as exc:
        with (run_dir / "cleanup.log").open("a", encoding="utf-8") as log:
            log.write(f"Cleanup failed: {type(exc).__name__}\n")
        warnings.warn(f"Docker cleanup incomplete; see {run_dir / 'cleanup.log'}", RuntimeWarning)


def remove_task_sandboxes(docker_host: str, run_dir: Path, task_id: str) -> None:
    """Remove only this completed task's recorded Agent and verifier containers."""
    _remove_sandbox_containers(docker_host, run_dir, task_id=task_id)


def _remove_sandbox_containers(
    docker_host: str, run_dir: Path, *, task_id: str | None = None,
) -> None:
    """Remove recorded IDs only after checking their exact run-owned names."""
    records_dir = run_dir / CONTAINER_RECORDS_DIR
    if task_id is not None:
        records_dir = records_dir / task_id
    records = list(records_dir.rglob("*.cid"))
    if not records:
        return
    client = None
    errors = []
    try:
        import docker

        client = docker.DockerClient(base_url=docker_host, timeout=30)
        for record in records:
            try:
                name = record.stem
                container_id = record.read_text(encoding="utf-8").strip()
                if not container_belongs_to_run(name, run_dir.name):
                    raise ValueError(f"{record.name}: name does not belong to this run")
                if not re.fullmatch(r"[0-9a-f]{64}", container_id):
                    raise ValueError(f"{record.name}: invalid container ID")
                container = client.api.inspect_container(container_id)
                if container["Id"] != container_id or container["Name"].lstrip("/") != name:
                    raise ValueError(f"{record.name}: container identity does not match its record")
                client.api.remove_container(container_id, force=True, v=True)
                record.unlink(missing_ok=True)
            except docker.errors.NotFound:
                record.unlink(missing_ok=True)
            except Exception as exc:
                errors.append(f"{type(exc).__name__}: {exc}")
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        if client is not None:
            try:
                client.close()
            except Exception as exc:
                errors.append(f"{type(exc).__name__}: {exc}")
    if errors:
        with (run_dir / "cleanup.log").open("a", encoding="utf-8") as log:
            for error in errors:
                log.write(f"Sandbox container cleanup failed: {error}\n")
        warnings.warn(
            f"Sandbox cleanup incomplete; see {run_dir / 'cleanup.log'}", RuntimeWarning
        )


def _pid_uses_socket(pid: int, socket_path: str) -> bool:
    try:
        environment = Path(f"/proc/{pid}/environ").read_bytes().split(b"\0")
    except FileNotFoundError:
        return False
    if f"DOCKER_RT_SOCK={socket_path}".encode() not in environment:
        raise RuntimeError("Daemon PID belongs to a different socket; refusing cleanup")
    return True


def _stop_owned_pid(pid: int, state: dict, run_dir: Path) -> None:
    stop_pid_file = Path(state["socket_dir"]) / "stop.pid"
    try:
        stop_pid_file.write_text(str(pid), encoding="utf-8")
        environment = os.environ.copy()
        environment["DOCKER_RT_SOCK"] = state["socket"]
        environment["DOCKER_CONFIG"] = state["docker_config"]
        with (run_dir / "cleanup.log").open("a", encoding="utf-8") as log:
            result = subprocess.run(
                [sys.executable, "-m", "pyromind_sdk.docker_rt.server", "--stop",
                 "--sock", state["socket"], "--pid-file", str(stop_pid_file)],
                env=environment, stdout=log, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, timeout=30, check=False,
            )
        if result.returncode:
            raise RuntimeError("Owned docker-rt daemon did not stop")
    finally:
        stop_pid_file.unlink(missing_ok=True)
