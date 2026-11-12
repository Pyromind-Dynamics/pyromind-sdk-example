"""Run the existing mini-swe-agent version against a Pier-owned sandbox."""

import argparse
import json
import logging
from pathlib import Path
import re
import shlex

import litellm
from minisweagent.agents.default import DefaultAgent
from minisweagent.config import builtin_config_dir, get_config_from_spec
from minisweagent.environments.docker import DockerEnvironment, DockerEnvironmentConfig
from minisweagent.models import get_model


class AttachedEnvironment(DockerEnvironment):
    """Use the sandbox supplied by Pier; only Pier owns its lifecycle."""

    def __init__(self, container_id: str):
        self.config = DockerEnvironmentConfig(image="pier-owned", cwd="/app", timeout=300)
        self.container_id = container_id
        self.logger = logging.getLogger(__name__)

    def cleanup(self):
        pass


def git_output(environment, command: str) -> str:
    result = environment.execute({"command": command})
    if result["returncode"]:
        raise RuntimeError(f"Cannot inspect agent submission: {result['output']}")
    return result["output"].rstrip("\r\n")


def git_commit(environment) -> str:
    value = git_output(environment, "git rev-parse --verify HEAD").strip()
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", value):
        raise ValueError(f"Invalid Git commit returned by sandbox: {value!r}")
    return value


def record_submission(environment, path: Path, initial_commit: str | None):
    """Inspect the agent's commits without staging or committing any files."""
    errors = {}
    try:
        head = git_commit(environment)
    except Exception as exc:
        head = None
        errors["submitted_commit"] = str(exc)
    submission = {
        "initial_commit": initial_commit,
        "submitted_commit": head,
        "has_new_commit": head != initial_commit if head and initial_commit else None,
    }
    commands = {"worktree_status": "git --no-optional-locks status --short --untracked-files=all"}
    if initial_commit and head:
        refs = f"{shlex.quote(initial_commit)} {shlex.quote(head)} --"
        commands["committed_files"] = f"git diff --no-ext-diff --no-textconv --name-status {refs}"
        commands["diff_stat"] = f"git diff --no-ext-diff --no-textconv --stat {refs}"
    for key, command in commands.items():
        try:
            submission[key] = git_output(environment, command)
        except Exception as exc:
            errors[key] = str(exc)
    if errors:
        submission["diagnostic_errors"] = errors
    path.write_text(json.dumps(submission, ensure_ascii=False, indent=2) + "\n")
    if submission["has_new_commit"] is False:
        logging.getLogger(__name__).warning(
            "Agent created no commit. Uncommitted changes will not be included in the DeepSWE patch."
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--instruction", type=Path, required=True)
    parser.add_argument("--container", required=True)
    parser.add_argument("--trajectory", type=Path, required=True)
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    official = get_config_from_spec(builtin_config_dir / "mini.yaml")
    environment = AttachedEnvironment(args.container)
    model = get_model(config={
        **official["model"],
        "model_class": "litellm", "model_name": f"openai/{config['model_name']}",
        "cost_tracking": "ignore_errors",
        "model_kwargs": {**official["model"].get("model_kwargs", {}),
                         "custom_llm_provider": "openai", "api_base": config["endpoint"],
                         "drop_params": True, "timeout": 300},
    })
    # HTTP 400 requests cannot be repaired by retrying the same conversation.
    model.abort_exceptions = [*model.abort_exceptions, litellm.exceptions.BadRequestError]
    agent = DefaultAgent(
        model, environment, step_limit=300, cost_limit=9999,
        wall_time_limit_seconds=0, output_path=args.trajectory,
        system_template=(
            "You are a software engineering agent. Use the bash tool to inspect "
            "the repository, implement the requested behavior and test your changes. "
            "Commands execute in /app in a new shell each time. "
            "Before finishing, review git status and git diff, explicitly stage "
            "the intended changes, and commit them. Include necessary new source, "
            "tests and resources; keep incidental build outputs, caches and "
            "temporary backups out of the commit. DeepSWE grades only committed "
            "changes; uncommitted work is not collected, and the evaluator will "
            "not commit files for you. If Git identity is unset, use "
            "git -c user.name=mini-swe-agent -c user.email=agent@localhost commit. "
            "Commit completed, tested changes as you work. "
            "When finished, run exactly: echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"
        ),
        instance_template="Implement the following task in /app:\n\n{{task}}",
    )
    initial_commit = None
    try:
        initial_commit = git_commit(environment)
    except Exception as exc:
        logging.getLogger(__name__).warning("Cannot record initial Git commit: %s", exc)
    info = {}
    try:
        info = agent.run(args.instruction.read_text())
    except Exception as exc:
        info = {"exit_status": type(exc).__name__, "exception_str": str(exc)}
        raise
    finally:
        agent.save(args.trajectory, {"instance_id": args.task_id, "info": info})
        try:
            record_submission(environment, args.trajectory.with_name("submission.json"), initial_commit)
        except Exception as exc:
            # Diagnostics must not replace the agent result or change grading.
            logging.getLogger(__name__).warning("Cannot record Git submission details: %s", exc)


if __name__ == "__main__":
    main()
