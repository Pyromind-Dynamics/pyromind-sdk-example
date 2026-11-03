"""Prepare a Docker CLI and start the PyroMind docker-rt daemon for SWE-bench."""

import os
import subprocess
import tempfile
from pathlib import Path


DOCKER_CLI_URL = "https://download.docker.com/linux/static/stable/x86_64/docker-27.5.1.tgz"
DOCKER_CLI_PATH = Path("/usr/local/bin/docker")
DOCKER_RT_SOCKET = "/tmp/docker-rt.sock"


def _install_docker_cli() -> None:
    """Install the requested Docker CLI version if the target has no CLI."""
    if DOCKER_CLI_PATH.is_file() and os.access(DOCKER_CLI_PATH, os.X_OK):
        return

    with tempfile.TemporaryDirectory(prefix="docker-cli-") as temporary_dir:
        archive = Path(temporary_dir) / "docker.tgz"
        with archive.open("wb") as destination:
            subprocess.run(["curl", "-fsSL", DOCKER_CLI_URL], stdout=destination, check=True)
        subprocess.run(
            ["tar", "-xz", "-C", temporary_dir, "docker/docker"], check=True
        )

        command = ["install", "-m", "755", str(Path(temporary_dir) / "docker/docker"), str(DOCKER_CLI_PATH)]
        if os.geteuid() != 0:
            command = ["sudo", "-n", *command]
        subprocess.run(command, check=True)


def prepare_docker_context(pyromind_api_key: str, cluster: str = "us-west-1#pre", log_file: str = "/workspace/docker-watch.log") -> str:
    """Start docker-rt and return the Docker host URL for benchmark subprocesses."""
    if not pyromind_api_key.strip():
        raise ValueError("pyromind_api_key must not be empty")
    if not cluster.strip():
        raise ValueError("cluster must not be empty")
    if not log_file.strip():
        raise ValueError("log_file must not be empty")

    log_path = Path(log_file).expanduser().resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    _install_docker_cli()

    environment = os.environ.copy()
    environment["PATH"] = f"{DOCKER_CLI_PATH.parent}{os.pathsep}{environment.get('PATH', '')}"
    environment["DOCKER_RT_SOCK"] = DOCKER_RT_SOCKET
    environment.pop("DOCKER_HOST", None)
    environment["PYROMIND_DOCKER_RT_SKIP_WRAPPER_PROMPT"] = "1"
    command = [
        "pyromind", "docker-rt", "--daemon",
        "--apikey", pyromind_api_key.strip(),
        "--cluster", cluster.strip(),
        "--log-file", str(log_path),
    ]
    result = subprocess.run(command, env=environment, check=False)
    if result.returncode != 0:
        # Avoid including the API key from command in an exception message.
        raise RuntimeError(f"docker-rt failed to start; see {log_path}")
    return f"unix://{DOCKER_RT_SOCKET}"
