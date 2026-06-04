"""CLI: run a workflow from a JSON file, wait for completion, export node I/O."""

import argparse
import json
import sys
import time
from pathlib import Path

import requests
from pyromind_sdk import PyroMindAPIClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Submit a workflow JSON to PyroMind and wait for results."
    )
    parser.add_argument("workflow", type=str, help="Path to workflow JSON file")
    parser.add_argument("--name", type=str, default=None,
                        help="Task name (default: workflow file name)")
    parser.add_argument("--output", type=str, default=None,
                        help="Output results file (default: <workflow_name>_result.json)")
    parser.add_argument("--poll-interval", type=int, default=5,
                        help="Poll interval in seconds (default: 5)")
    parser.add_argument("--timeout", type=int, default=600,
                        help="Max wait time in seconds (default: 600)")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty-print JSON output")
    parser.add_argument("--max-retries", type=int, default=0,
                        help="Max retries for API requests (default: 0)")
    return parser.parse_args()


def load_workflow(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"Error: file not found: {p}", file=sys.stderr)
        sys.exit(1)
    with open(p) as f:
        return json.load(f)


def _raw_create(client, workflow_body: dict, task_name: str):
    """Make a direct HTTP request and return raw response (bypasses SDK retry)."""
    url = f"{client.studio.base_url.rstrip('/')}/studio/tasks"
    headers = dict(client.studio.session.headers)
    payload = {"name": task_name, "workflow": workflow_body}
    try:
        return requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        if e.response is not None:
            print(f"Status: {e.response.status_code}", file=sys.stderr)
            for k, v in sorted(e.response.headers.items()):
                print(f"  {k}: {v}", file=sys.stderr)
        return None


def _todict(obj):
    return obj if isinstance(obj, dict) else obj.model_dump()

def export_node_outputs(client, task_id: str, nodes_info: list, workflow_nodes: list) -> list:
    wf_by_name = {}
    for wn in workflow_nodes:
        nd = wn.get("data", {})
        wf_by_name[f"#{nd.get('id') or wn.get('id', '?')}"] = nd.get("config", {})

    results = []
    for node in nodes_info:
        nd = _todict(node)
        node_id = nd.get("node_id") or nd.get("id")
        node_name = nd.get("node_name") or str(node_id)
        entry = {
            "node_name": node_name,
            "node_id": node_id,
            "start_at": nd.get("start_at"),
            "end_at": nd.get("end_at"),
            "duration": str(nd.get("duration", "")),
            "input": wf_by_name.get(node_name, {}),
        }
        try:
            output = client.studio.get_node_output(str(task_id), str(node_id))
            if output:
                output.pop("exit_code", None)
                params = output.pop("parameters", [])
                entry["output"] = {p["name"]: p.get("value", "") for p in params}
                entry["raw"] = output
            else:
                entry["output"] = None
        except Exception as e:
            entry["output_error"] = str(e)
        results.append(entry)
    return results


def main():
    args = parse_args()

    workflow = load_workflow(args.workflow)
    task_name = args.name or workflow.get("name") or Path(args.workflow).stem

    output_dir = Path(__file__).resolve().parent / "tests" / "test_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output or str(output_dir / f"{task_name}_result.json")

    client = PyroMindAPIClient(max_retries=args.max_retries)

    print(f"Creating task '{task_name}' ...")
    raw_resp = _raw_create(client, workflow, task_name)
    if raw_resp is None:
        sys.exit(1)
    print(f"Response: {raw_resp.status_code}")
    for k in ("content-type", "x-request-id", "x-cluster", "server", "date"):
        v = raw_resp.headers.get(k)
        if v:
            print(f"  {k}: {v}")
    if not raw_resp.ok:
        body = raw_resp.json()
        err = body.get("error") or body.get("detail") or raw_resp.text[:500]
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
    resp_data = raw_resp.json()
    task_id = resp_data["data"]["task_id"]
    print(f"Task created: {task_id}")

    deadline = time.time() + args.timeout
    final_status = None

    while time.time() < deadline:
        time.sleep(args.poll_interval)
        job = client.studio.get_job(task_id)
        status = (getattr(job, "status", "") or "").lower()
        print(f"  status: {status}")
        if status in ("completed", "succeeded"):
            final_status = "success"
            break
        if status in ("failed", "error", "cancelled", "stopped"):
            final_status = status
            break

    if final_status is None:
        final_status = "timeout"
        print(f"Timed out after {args.timeout}s")

    result = {
        "task_id": task_id,
        "task_name": task_name,
        "status": final_status,
        "error_message": getattr(job, "error_message", None) if final_status != "success" else None,
    }

    nodes_info = getattr(job, "nodes", []) or []
    if isinstance(nodes_info, list):
        result["nodes"] = export_node_outputs(
            client, task_id, nodes_info,
            workflow.get("nodes", []),
        )

    indent = 2 if args.pretty else None
    output = json.dumps(result, indent=indent, ensure_ascii=False, default=str)
    print(f"\nResult:\n{output}")

    with open(output_path, "w") as f:
        f.write(output)
    print(f"\nSaved to {output_path}")


if __name__ == "__main__":
    main()
