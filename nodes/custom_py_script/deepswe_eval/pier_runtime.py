"""Pier adapters for the existing Docker CLI / PyroMind docker-rt workflow.

The agent runs on the evaluation host, as in minisweBenchmark. Only task
commands run in the sandbox; model credentials are never copied into it.
"""

import asyncio
import json
import math
import os
from pathlib import Path
import re
import shlex
import signal
import sys
from uuid import uuid4

from pier.agents.base import BaseAgent
from pier.environments.base import BaseEnvironment, ExecResult
from pier.environments.capabilities import EnvironmentCapabilities
from sandbox_tracking import record_container


async def run_process(*args, timeout=300, cwd=None, env=None):
    process = await asyncio.create_subprocess_exec(
        *map(str, args), cwd=cwd, env=env, start_new_session=True,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
    except BaseException:
        if process.returncode is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                await asyncio.wait_for(process.wait(), 5)
            except asyncio.TimeoutError:
                os.killpg(process.pid, signal.SIGKILL)
                await process.wait()
        raise
    return ExecResult(stdout=stdout.decode(errors="replace"),
                      stderr=stderr.decode(errors="replace"), return_code=process.returncode)


class DockerRuntimeEnvironment(BaseEnvironment):
    """Use prebuilt task images without requiring Docker Compose or builds."""

    def __init__(self, *args, run_dir: str, run_id: str, runtime_kind="pyromind", **kwargs):
        self.run_dir = Path(run_dir)
        self.run_id = run_id
        self.runtime_kind = runtime_kind
        self.container_id = None
        self.container_name = f"minisweagent-{run_id}-{uuid4().hex[:8]}"
        self.is_verifier = Path(kwargs["environment_dir"]).name == "tests"
        super().__init__(*args, **kwargs)

    @staticmethod
    def type():
        return "pyromind-docker-rt"

    @property
    def capabilities(self):
        return EnvironmentCapabilities(disable_internet=self.runtime_kind == "docker")

    def _validate_internet_config(self):
        if self.runtime_kind == "pyromind" and not self.task_env_config.allow_internet:
            # SDK 0.1.15 does not implement Docker NetworkMode=none. Do not
            # pretend that the daemon can enforce the official network policy.
            self.logger.warning(
                "docker-rt network isolation is platform-managed, not enforced "
                "by this adapter. This is a local evaluation, not an official leaderboard run."
            )
        else:
            super()._validate_internet_config()

    def _validate_definition(self):
        if self.task_os.value != "linux":
            raise ValueError("DeepSWE adapter supports Linux task images only")
        if not self.task_env_config.docker_image and not self.is_verifier:
            raise ValueError("DeepSWE task requires a prebuilt docker_image")
        if self.agent_install_spec:
            raise ValueError("Use HostMiniSweAgent; in-sandbox agent installs are unsupported")
        if self.is_verifier:
            # These pinned v1.1 Dockerfiles only copy tests into the pristine
            # task image. Refuse future build steps instead of skipping them.
            lines = [line.strip() for line in (self.environment_dir / "Dockerfile").read_text().splitlines()
                     if line.strip() and not line.lstrip().startswith("#")]
            sources = [line for line in lines if line.startswith("FROM ")]
            if len(sources) != 1 or not re.fullmatch(r"FROM\s+\S+", sources[0]):
                raise ValueError("Verifier Dockerfile must use one pinned task image")
            for line in lines:
                if line.startswith("FROM ") or line == "RUN chmod +x /tests/test.sh":
                    continue
                parts = shlex.split(line)
                if len(parts) != 3 or parts[0] != "COPY" or not parts[2].startswith("/tests/"):
                    raise ValueError(f"Unsupported verifier build instruction: {line}")

    async def _docker(self, *args, timeout=300):
        return await run_process("/usr/local/bin/docker", *args, timeout=timeout)

    async def _checked(self, *args, timeout=300):
        result = await self._docker(*args, timeout=timeout)
        if result.return_code:
            raise RuntimeError(f"Docker {args[0]} failed: {result.stderr or result.stdout}")
        return result

    def resource_limits(self):
        """Fit PyroMind's 1 CPU : 2 GiB rule without reducing task resources."""
        cpus = self.task_env_config.cpus
        memory_mb = self.task_env_config.memory_mb
        if self.runtime_kind == "pyromind":
            cpus = max(cpus or 1, math.ceil((memory_mb or 0) / 2048))
            memory_mb = cpus * 2048
        return cpus, memory_mb

    async def start(self, force_build=False):
        if force_build:
            raise ValueError("DeepSWE uses pinned prebuilt images; force_build is unsupported")
        image = self.task_env_config.docker_image
        if not image and self.is_verifier:
            # v1.1 verifier config specifies resources; tests/Dockerfile pins
            # the pristine base image. Upload only tests/, never solution/.
            dockerfile = (self.environment_dir / "Dockerfile").read_text()
            match = re.search(r"^FROM\s+(\S+)\s*$", dockerfile, re.MULTILINE)
            if not match:
                raise ValueError("Verifier Dockerfile must use a pinned task image")
            image = match.group(1)
        if not image:
            raise ValueError("Missing prebuilt image")
        cpus, memory_mb = self.resource_limits()
        requested = {"cpus": self.task_env_config.cpus, "memory_mb": self.task_env_config.memory_mb}
        allocated = {"cpus": cpus, "memory_mb": memory_mb}
        phase = "verifier" if self.is_verifier else "agent"
        self.trial_paths.trial_dir.mkdir(parents=True, exist_ok=True)
        (self.trial_paths.trial_dir / f"resources-{phase}.json").write_text(json.dumps({
            "runtime_kind": self.runtime_kind, "requested": requested, "allocated": allocated,
        }, indent=2) + "\n")
        if allocated != requested:
            self.logger.warning("Platform resource mapping: requested=%s, allocated=%s", requested, allocated)
        args = ["run", "-d", "--name", self.container_name, "--workdir", "/app"]
        if cpus:
            args += ["--cpus", str(cpus)]
        if memory_mb:
            args += ["--memory", f"{memory_mb}m"]
        if self.runtime_kind == "docker" and not self.task_env_config.allow_internet:
            args += ["--network", "none"]
        for key, value in (self._merge_env(None) or {}).items():
            args += ["--env", f"{key}={value}"]
        # cidfile records ownership even if startup fails after creation.
        records = self.run_dir / "sandbox-containers" / self.trial_paths.trial_dir.name
        records.mkdir(parents=True, exist_ok=True)
        args += ["--cidfile", str(records / f"{self.container_name}.cid"),
                 "--entrypoint", "sleep", image, "12h"]
        result = await self._checked(*args, timeout=self.task_env_config.build_timeout_sec)
        self.container_id = result.stdout.strip()
        record_container(self.run_dir, self.container_name, self.container_id,
                         task_id=self.trial_paths.trial_dir.name)
        result = await self.exec("mkdir -p /logs/agent /logs/verifier /logs/artifacts /tests")
        if result.return_code:
            raise RuntimeError("Cannot prepare sandbox log directories")
        if self.is_verifier:
            await self.upload_dir(self.environment_dir, "/tests")

    async def stop(self, delete=True):
        if self.container_id is None:
            return
        await self._checked("rm", "-f", self.container_id, timeout=120)
        self.container_id = None

    async def exec(self, command, cwd=None, env=None, timeout_sec=None, user=None):
        if self.container_id is None:
            raise RuntimeError("Sandbox is not running")
        args = ["exec", "--workdir", cwd or self.task_env_config.workdir or "/app"]
        effective_user = self._resolve_user(user)
        if effective_user is not None:
            if self.runtime_kind == "pyromind" and str(effective_user) in {"root", "0", "0:0", "root:root"}:
                identity = await self._checked("exec", self.container_id, "id", "-u")
                if identity.stdout.strip() != "0":
                    raise RuntimeError("docker-rt sandbox must run as root for verifier setup")
            else:
                args += ["--user", str(effective_user)]
        for key, value in (self._merge_env(env) or {}).items():
            args += ["--env", f"{key}={value}"]
        # A sandbox-side timeout also stops the remote exec when the local
        # client is cancelled or times out.
        seconds = max(1, int(timeout_sec or 1800))
        args += [self.container_id, "timeout", "--kill-after=5", str(seconds), "bash", "-lc", command]
        return await self._docker(*args, timeout=seconds + 30)

    async def upload_file(self, source_path, target_path):
        if self.runtime_kind == "pyromind" and Path(source_path).is_file() and Path(source_path).stat().st_size == 0:
            # docker-rt's chunked upload rejects zero chunks. Preserve the empty
            # artifact so the official verifier can grade the pristine base.
            parent = shlex.quote(str(Path(target_path).parent))
            target = shlex.quote(str(target_path))
            result = await self.exec(f"mkdir -p {parent} && : > {target}")
            if result.return_code:
                raise RuntimeError(f"Cannot create empty artifact: {result.stderr or result.stdout}")
            return
        await self._checked("cp", str(source_path), f"{self.container_id}:{target_path}")

    async def upload_dir(self, source_dir, target_dir):
        result = await self.exec(f"mkdir -p {shlex.quote(str(target_dir))}")
        if result.return_code:
            raise RuntimeError("Cannot create upload directory")
        source = Path(source_dir)
        if self.runtime_kind == "pyromind" and any(p.is_file() and p.stat().st_size == 0 for p in source.rglob("*")):
            # Pier uploads the whole artifact directory, including model.patch.
            # Traverse only directories needing the empty-file workaround.
            for path in sorted(source.iterdir()):
                target = str(Path(target_dir) / path.name)
                if path.is_dir():
                    await self.upload_dir(path, target)
                else:
                    await self.upload_file(path, target)
        else:
            await self._checked("cp", f"{source}/.", f"{self.container_id}:{target_dir}")

    async def download_file(self, source_path, target_path):
        Path(target_path).parent.mkdir(parents=True, exist_ok=True)
        await self._checked("cp", f"{self.container_id}:{source_path}", str(target_path))

    async def download_dir(self, source_dir, target_dir):
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        await self._checked("cp", f"{self.container_id}:{source_dir}/.", str(target_dir))


class HostMiniSweAgent(BaseAgent):
    """Keep inference on the host and delegate sandbox commands via docker-rt."""

    @staticmethod
    def name():
        return "mini-swe-agent"

    def version(self):
        from importlib.metadata import version
        return version("mini-swe-agent")

    async def setup(self, environment):
        pass

    async def run(self, instruction, environment, context):
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        instruction_path = self.logs_dir / "instruction.txt"
        instruction_path.write_text(instruction)
        native_path = self.logs_dir / "mini-swe-agent.trajectory.json"
        task_id = self.logs_dir.parent.name
        config = json.loads(Path(os.environ["DEEPSWE_RUN_CONFIG"]).read_text())
        task_timeout = config.get("agent_timeouts", {}).get(task_id, 10800)
        try:
            result = await run_process(
                sys.executable, Path(__file__).with_name("run_agent.py"),
                "--config", os.environ["DEEPSWE_RUN_CONFIG"],
                "--instruction", instruction_path, "--container", environment.container_id,
                "--trajectory", native_path, "--task-id", task_id,
                timeout=task_timeout + 60,
            )
            (self.logs_dir / "agent-stdout.txt").write_text(result.stdout + result.stderr)
            if result.return_code:
                info = json.loads(native_path.read_text()).get("info", {}) if native_path.is_file() else {}
                detail = info.get("exception_str") or "mini-swe-agent failed"
                raise RuntimeError(f"{detail}; see {self.logs_dir / 'agent-stdout.txt'}")
        finally:
            if native_path.is_file():
                native = json.loads(native_path.read_text())
                context.n_agent_steps = sum(m.get("role") == "assistant" for m in native.get("messages", []))
                context.metadata = {"native_trajectory_path": str(native_path)}
