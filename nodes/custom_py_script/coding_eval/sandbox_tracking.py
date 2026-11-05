"""Record sandbox ownership for one evaluation run."""

import os
import re
import sys
from pathlib import Path


CONTAINER_RECORDS_DIR = "sandbox-containers"


def container_belongs_to_run(name: str, run_id: str) -> bool:
    run = re.escape(run_id)
    return re.fullmatch(
        rf"(?:minisweagent-{run}-[0-9a-f]{{8}}|sweb\.eval\.[a-zA-Z0-9_.-]+\.{run}(?:\.\d+)?)",
        name,
    ) is not None


def record_container(run_dir: Path, name: str, container_id: str) -> None:
    records_dir = run_dir / CONTAINER_RECORDS_DIR
    records_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    (records_dir / f"{name}.cid").write_text(container_id + "\n", encoding="utf-8")


def write_agent_docker_launcher(runs_dir: Path, run_id: str, docker_cli: Path) -> Path:
    """Give mini-swe-agent a Docker executable that records each created ID."""
    launcher = runs_dir / "docker-agent"
    launcher.write_text(
        f"#!{sys.executable}\n"
        "import sys\n"
        f"sys.path.insert(0, {str(Path(__file__).resolve().parent)!r})\n"
        "from sandbox_tracking import agent_docker_main\n"
        f"agent_docker_main({str(runs_dir.parent)!r}, {run_id!r}, {str(docker_cli)!r})\n",
        encoding="utf-8",
    )
    launcher.chmod(0o700)
    return launcher


def agent_docker_main(run_dir: str, run_id: str, docker_cli: str) -> None:
    args = sys.argv[1:]
    if args[0] == "run":
        name_index = args.index("--name") + 1
        original_name = args[name_index]
        name = f"minisweagent-{run_id}-{original_name.removeprefix('minisweagent-')}"
        args[name_index] = name
        records_dir = Path(run_dir) / CONTAINER_RECORDS_DIR
        records_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        # The Docker CLI writes the ID after creation, before starting the container.
        args[1:1] = ["--cidfile", str(records_dir / f"{name}.cid")]
    os.execv(docker_cli, [docker_cli, *args])
