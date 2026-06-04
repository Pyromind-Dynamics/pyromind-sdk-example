"""Validate and run workflows for specific nodes."""
import argparse
import json
import os
import re
import sys
from pathlib import Path

from pyromind_sdk import PyroMindAPIClient
from pyromind_sdk.client.models import TrainingTaskCreateRequest

NODES = ["LoadImage", "LoadDataset"]

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"
WORKFLOW_DIR = Path(__file__).resolve().parents[1] / "workflow"
RESULTS_DIR = Path(__file__).resolve().parent / "test_output"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_FILE = RESULTS_DIR / "single_node_results.json"


def _extract_type(raw_type) -> str:
    if isinstance(raw_type, list):
        if len(raw_type) == 0:
            return "STRING"
        first = raw_type[0]
        if isinstance(first, str) and first.isupper():
            return first
        return "STRING"
    return str(raw_type).upper()


def parse_markdown_table(table_text: str) -> dict[str, str]:
    rows = [line.strip() for line in table_text.strip().split("\n") if line.strip()]
    if len(rows) < 3:
        return {}
    result = {}
    for row in rows[2:]:
        cols = [c.strip() for c in row.split("|") if c.strip()]
        if len(cols) >= 2:
            result[cols[0]] = cols[1]
    return result


def extract_node_spec_from_docs(node_name: str) -> dict | None:
    doc_file = DOCS_DIR / node_name / f"{node_name}.md"
    if not doc_file.exists():
        return None
    text = doc_file.read_text()
    result = {}

    input_match = re.search(
        r"##\s+.*Input\s*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL
    )
    if input_match:
        result["input"] = parse_markdown_table(input_match.group(1))

    output_match = re.search(
        r"##\s+.*Output\s*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL
    )
    if output_match:
        result["output"] = parse_markdown_table(output_match.group(1))

    return result if result else None


def build_sdk_inputs(info: dict) -> dict[str, str]:
    inputs = {}
    for section in ("required", "optional"):
        for name, spec in info.get("input", {}).get(section, {}).items():
            raw_type = spec[0] if isinstance(spec, list) else spec
            inputs[name] = _extract_type(raw_type)
    return inputs


def build_sdk_outputs(info: dict) -> dict[str, str]:
    outputs = {}
    names = info.get("output_name", [])
    types = info.get("output", [])
    for i, name in enumerate(names):
        raw_type = types[i] if i < len(types) else ""
        outputs[name] = _extract_type(raw_type)
    return outputs


def try_run_workflow(client, node_name: str) -> dict:
    result = {"node": node_name, "status": "skipped", "task_id": None, "message": None}
    workflow_file = WORKFLOW_DIR / node_name / f"{node_name}.json"
    if not workflow_file.exists():
        result["message"] = "no workflow file"
        return result

    try:
        with open(workflow_file) as f:
            workflow_data = json.load(f)
    except Exception as e:
        result["status"] = "error"
        result["message"] = f"failed to read workflow file — {e}"
        return result

    try:
        result_data = client.studio.create_and_wait(
            TrainingTaskCreateRequest(
                name=f"test_{node_name}",
                workflow=workflow_data,
            ),
            timeout=300,
            check_interval=3,
        )
        task_id = result_data["task_id"]
        status = result_data["status"]
        result["task_id"] = task_id
        result["status"] = status
        if status == "success":
            result["message"] = "workflow succeeded"
        elif status == "timeout":
            result["message"] = "timed out after 300s"
        else:
            result["message"] = f"workflow ended with status={status}"
        return result
    except Exception as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            return result
        result["status"] = "error"
        result["message"] = f"workflow create/poll failed — {e}"
        return result


def get_nodes() -> list[str]:
    env_nodes = os.environ.get("PYROMIND_NODES")
    if env_nodes:
        return [n.strip() for n in env_nodes.split(",") if n.strip()]
    return NODES


def validate_node(node_name: str, client, sdk_nodes):
    if not isinstance(sdk_nodes, dict):
        print(f"Error: Expected dict, got {type(sdk_nodes)}", file=sys.stderr)
        return False

    info = sdk_nodes.get(node_name)
    if info is None:
        print(f"Error: Node '{node_name}' not found in SDK", file=sys.stderr)
        return False

    spec = extract_node_spec_from_docs(node_name)
    mismatches = []

    if spec is None:
        print(f"  [SKIP] No docs for node '{node_name}'")
        return None

    sdk_inputs = build_sdk_inputs(info)
    sdk_outputs = build_sdk_outputs(info)

    for param, dtype in spec.get("input", {}).items():
        dtype = dtype.split("(")[0].strip().upper()
        if param in sdk_inputs:
            if sdk_inputs[param] != dtype:
                mismatches.append(f"input.{param}: doc={dtype}, sdk={sdk_inputs[param]}")
        else:
            mismatches.append(f"input.{param}: in docs but missing from SDK")

    for param, dtype in spec.get("output", {}).items():
        dtype = dtype.split("(")[0].strip().upper()
        if param in sdk_outputs:
            if sdk_outputs[param] != dtype:
                mismatches.append(f"output.{param}: doc={dtype}, sdk={sdk_outputs[param]}")
        else:
            mismatches.append(f"output.{param}: in docs but missing from SDK")

    if mismatches:
        print(f"\n  Type mismatches for '{node_name}':")
        for m in mismatches:
            print(f"    - {m}")
        return False

    return True


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate node docs and run workflows for specific nodes."
    )
    parser.add_argument("--node", "-k", type=str, default=None,
                        help="Filter nodes by name (supports 'LoadImage or LoadDataset' syntax)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    return parser.parse_args()


def main():
    args = parse_args()

    client = PyroMindAPIClient()
    sdk_nodes = client.studio.get_node_info()

    all_nodes = get_nodes()
    if args.node:
        filters = [n.strip() for n in args.node.replace("or", ",").split(",") if n.strip()]
        nodes_to_test = [n for n in all_nodes if any(f == n for f in filters)]
    else:
        nodes_to_test = all_nodes

    if not nodes_to_test:
        print("No nodes to test.", file=sys.stderr)
        sys.exit(1)

    results = []
    passed = 0
    failed = 0
    skipped = 0

    for node_name in nodes_to_test:
        print(f"\n=== {node_name} ===")
        valid = validate_node(node_name, client, sdk_nodes)

        if valid is None:
            skipped += 1
            wf_result = {"status": "skipped", "message": "no docs"}
        elif valid:
            passed += 1
            wf_result = try_run_workflow(client, node_name)
        else:
            failed += 1
            wf_result = try_run_workflow(client, node_name)

        print(f"  Workflow: {wf_result['status']} — {wf_result.get('message', '')}")
        results.append({"node": node_name, "validation": "passed" if valid else ("skipped" if valid is None else "failed"), "workflow": wf_result})

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDone: {passed} passed, {failed} failed, {skipped} skipped")
    print(f"Results saved to {RESULTS_FILE}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
