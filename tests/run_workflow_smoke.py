"""Run one workflow, export its node outputs, and optionally assert a result."""

from __future__ import annotations

import argparse
import json
import os
import uuid
from pathlib import Path

from pyromind_sdk import PyroMindAPIClient
from pyromind_sdk.client.models import TrainingTaskCreateRequest


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", type=Path, help="Workflow JSON path relative to the repo root")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--poll-interval", type=int, default=3)
    parser.add_argument("--expect-cluster", help="Fail if PYROMIND_CLUSTER differs from this value")
    parser.add_argument("--expect-result", help="Assert the single node's result output equals this value")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workflow_file = args.workflow
    if not workflow_file.is_absolute():
        workflow_file = REPO_ROOT / workflow_file
    if not workflow_file.is_file():
        raise FileNotFoundError(f"Workflow file not found: {workflow_file}")

    api_key = os.environ["PYROMIND_API_KEY"]
    base_url = os.environ["PYROMIND_BASE_URL"]
    cluster = os.environ["PYROMIND_CLUSTER"]
    if args.expect_cluster and cluster != args.expect_cluster:
        raise AssertionError(
            f"Expected PYROMIND_CLUSTER={args.expect_cluster!r}, got {cluster!r}"
        )

    workflow = json.loads(workflow_file.read_text(encoding="utf-8"))
    run_suffix = "-".join(
        (
            os.environ.get("GITHUB_RUN_ID", "local"),
            os.environ.get("GITHUB_RUN_ATTEMPT", uuid.uuid4().hex[:8]),
        )
    )
    task_name = f"ci-{workflow_file.stem}-{run_suffix}"
    client = PyroMindAPIClient(api_key=api_key, base_url=base_url, cluster=cluster)
    result = client.studio.create_and_wait(
        TrainingTaskCreateRequest(
            name=task_name,
            workflow=workflow,
            out_id=task_name,
        ),
        timeout=args.timeout,
        check_interval=args.poll_interval,
        export_node_outputs=True,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    if result.get("status") != "success":
        raise RuntimeError(
            f"Workflow {workflow_file.name} failed: "
            f"{result.get('error_message') or result.get('status')}"
        )

    if args.expect_result is not None:
        nodes = result.get("nodes") or []
        if len(nodes) != 1:
            raise AssertionError(f"Expected one node output, got {len(nodes)}")
        output = nodes[0].get("output") or {}
        actual = output.get("result")
        if not isinstance(actual, str) or not actual.strip():
            raise AssertionError(f"Workflow result is missing or empty: {output!r}")
        actual = actual.strip()
        print(f"Validated node result: {actual}")
        if actual != args.expect_result:
            raise AssertionError(
                f"Expected node result {args.expect_result!r}, got {actual!r}"
            )


if __name__ == "__main__":
    main()
