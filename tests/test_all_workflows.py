"""Run all workflow JSON files under workflow/ and report failures."""
import argparse
import json
import sys
from pathlib import Path

from pyromind_sdk import PyroMindAPIClient
from pyromind_sdk.client.models import TrainingTaskCreateRequest

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = REPO_ROOT / "workflow"
RESULTS_DIR = Path(__file__).resolve().parent / "test_output"
RESULTS_FILE = RESULTS_DIR / "all_workflow_results.json"


class WorkflowRunError(Exception):
    """One or more workflows failed to run successfully."""


def discover_workflows() -> list[Path]:
    return sorted(WORKFLOW_DIR.glob("*/*.json"))


def run_workflow(
    client: PyroMindAPIClient,
    workflow_file: Path,
    timeout: int,
    check_interval: int,
) -> dict:
    workflow_data = json.loads(workflow_file.read_text())
    node_name = workflow_file.parent.name
    result = {
        "workflow": str(workflow_file.relative_to(REPO_ROOT)),
        "node": node_name,
        "status": "error",
        "task_id": None,
        "message": None,
    }

    try:
        data = client.studio.create_and_wait(
            TrainingTaskCreateRequest(
                name=f"test_{node_name}",
                workflow=workflow_data,
            ),
            timeout=timeout,
            check_interval=check_interval,
        )
        result["task_id"] = data["task_id"]
        result["status"] = data["status"]
        if data["status"] == "success":
            result["message"] = "workflow succeeded"
        elif data["status"] == "timeout":
            result["message"] = f"timed out after {timeout}s"
        else:
            error_message = data.get("error_message")
            result["message"] = error_message or f"workflow ended with status={data['status']}"
    except Exception as e:
        result["message"] = str(e)

    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run all workflow JSON files under workflow/.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Max wait time per workflow in seconds (default: 300)",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=3,
        help="Poll interval in seconds (default: 3)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workflow_files = discover_workflows()
    if not workflow_files:
        raise FileNotFoundError(f"No workflow JSON files found under {WORKFLOW_DIR}")

    client = PyroMindAPIClient()
    results: list[dict] = []
    failures: list[dict] = []

    print(f"[INFO] Running {len(workflow_files)} workflows...", flush=True)
    for workflow_file in workflow_files:
        rel = workflow_file.relative_to(REPO_ROOT)
        print(f"[INFO] Running {rel}...", flush=True)
        result = run_workflow(client, workflow_file, args.timeout, args.poll_interval)
        results.append(result)
        print(
            f"[INFO] {rel}: {result['status']} — {result.get('message', '')}",
            flush=True,
        )
        if result["status"] != "success":
            failures.append(result)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    print(f"\n[INFO] Results saved to {RESULTS_FILE}")

    if failures:
        lines = "\n".join(
            f"  - {r['workflow']}: {r['status']} — {r['message']} (task_id={r['task_id']})"
            for r in failures
        )
        raise WorkflowRunError(
            f"Workflow failures ({len(failures)}/{len(results)}):\n{lines}"
        )

    print(f"\nAll {len(results)} workflows succeeded.")


if __name__ == "__main__":
    main()
