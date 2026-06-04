"""CLI: submit a workflow JSON to PyroMind and wait for results."""
import argparse
import json
from pathlib import Path

from pyromind_sdk import PyroMindAPIClient
from pyromind_sdk.client.models import TrainingTaskCreateRequest


def parse_args():
    parser = argparse.ArgumentParser(
        description="Submit a workflow JSON to PyroMind and wait for results."
    )
    parser.add_argument("workflow", type=str, nargs="?", default="workflow/LoadDataset/LoadDataset.json",
                        help="Path to workflow JSON file (default: workflow/LoadDataset/LoadDataset.json)")
    parser.add_argument("--name", type=str, default=None,
                        help="Task name (default: workflow file name)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output results file (default: tests/test_output/<name>_result.json)")
    parser.add_argument("--poll-interval", type=int, default=5,
                        help="Poll interval in seconds (default: 5)")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Max wait time in seconds (default: 600)")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output")
    parser.add_argument("--max-retries", type=int, default=0,
                        help="Max retries for API requests (default: 0)")
    return parser.parse_args()


def run_workflow(path: str, task_name: str | None = None, output: str | None = None,
                 timeout: int = 600, poll_interval: int = 5, pretty: bool = False,
                 max_retries: int = 0):
    workflow_file = Path(path)
    if not workflow_file.is_absolute():
        workflow_file = Path(__file__).resolve().parents[1] / workflow_file
    workflow = json.loads(workflow_file.read_text())

    task_name = task_name or workflow.get("name") or workflow_file.stem
    output_dir = Path(__file__).resolve().parent / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output or str(output_dir / f"{task_name}_result.json")

    client = PyroMindAPIClient(max_retries=max_retries)
    print(f"Creating task '{task_name}' ...")

    result = client.studio.create_and_wait(
        TrainingTaskCreateRequest(name=task_name, workflow=workflow),
        timeout=timeout,
        check_interval=poll_interval,
        export_node_outputs=True,
    )

    print(f"Task {result['task_id']}: {result['status']}")
    indent = 2 if pretty else None
    output_text = json.dumps(result, indent=indent, ensure_ascii=False, default=str)
    print(f"\n{output_text}")
    with open(output_path, "w") as f:
        f.write(output_text)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    args = parse_args()
    run_workflow(
        path=args.workflow,
        task_name=args.name,
        output=args.output,
        timeout=args.timeout,
        poll_interval=args.poll_interval,
        pretty=args.pretty,
        max_retries=args.max_retries,
    )
