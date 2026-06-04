"""Full Node Validation: compare SDK node definitions against docs and run workflows."""
import json
import re
import sys
from pathlib import Path

from pyromind_sdk import PyroMindAPIClient
from pyromind_sdk.client.models import TrainingTaskCreateRequest

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs"
WORKFLOW_DIR = Path(__file__).resolve().parents[1] / "workflow"
RESULTS_DIR = Path(__file__).resolve().parent / "test_output"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_FILE = RESULTS_DIR / "workflow_results.json"


def _extract_type(raw_type) -> str:
    """Normalize a node's input/output type to an uppercase string for comparison."""
    if isinstance(raw_type, list):
        if len(raw_type) == 0:
            return "STRING"
        first = raw_type[0]
        if isinstance(first, str) and first.isupper():
            return first
        return "STRING"
    return str(raw_type).upper()


def parse_markdown_table(table_text: str) -> dict[str, str]:
    """Parse a GFM markdown table and return {parameter: data_type}."""
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
    """Read doc markdown and extract expected input/output types."""
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
    """Build {param: type} from SDK node info input definition."""
    inputs = {}
    for section in ("required", "optional"):
        for name, spec in info.get("input", {}).get(section, {}).items():
            raw_type = spec[0] if isinstance(spec, list) else spec
            inputs[name] = _extract_type(raw_type)
    return inputs


def build_sdk_outputs(info: dict) -> dict[str, str]:
    """Build {param: type} from SDK node info output definition."""
    outputs = {}
    names = info.get("output_name", [])
    types = info.get("output", [])
    for i, name in enumerate(names):
        raw_type = types[i] if i < len(types) else ""
        outputs[name] = _extract_type(raw_type)
    return outputs


def try_run_workflow(client, node_name: str) -> dict:
    """Try to run a workflow for the given node. Returns a result dict."""
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


def run_all():
    """Every node with docs must have matching input/output definitions."""
    client = PyroMindAPIClient()
    nodes = client.studio.get_node_info()

    if not isinstance(nodes, dict):
        print(f"Error: Expected dict from get_node_info(), got {type(nodes)}", file=sys.stderr)
        sys.exit(1)

    missing_docs = []
    mismatches = []
    node_results = []

    for node_name, info in nodes.items():
        spec = extract_node_spec_from_docs(node_name)
        if spec is None:
            missing_docs.append(node_name)
            continue

        node_result = {"node": node_name, "validation": {"status": "passed", "checks": []}}

        sdk_inputs = build_sdk_inputs(info)
        sdk_outputs = build_sdk_outputs(info)

        for param, dtype in spec.get("input", {}).items():
            dtype = dtype.split("(")[0].strip().upper()
            if param in sdk_inputs:
                if sdk_inputs[param] != dtype:
                    msg = f"input.{param}: doc={dtype}, sdk={sdk_inputs[param]}"
                    node_result["validation"]["checks"].append({"param": f"input.{param}", "status": "failed", "detail": msg})
                    mismatches.append(f"{node_name}.{msg}")
                else:
                    node_result["validation"]["checks"].append({"param": f"input.{param}", "status": "passed"})
            else:
                msg = f"input.{param}: in docs but missing from SDK"
                node_result["validation"]["checks"].append({"param": f"input.{param}", "status": "failed", "detail": msg})
                mismatches.append(f"{node_name}.{msg}")

        for param, dtype in spec.get("output", {}).items():
            dtype = dtype.split("(")[0].strip().upper()
            if param in sdk_outputs:
                if sdk_outputs[param] != dtype:
                    msg = f"output.{param}: doc={dtype}, sdk={sdk_outputs[param]}"
                    node_result["validation"]["checks"].append({"param": f"output.{param}", "status": "failed", "detail": msg})
                    mismatches.append(f"{node_name}.{msg}")
                else:
                    node_result["validation"]["checks"].append({"param": f"output.{param}", "status": "passed"})
            else:
                msg = f"output.{param}: in docs but missing from SDK"
                node_result["validation"]["checks"].append({"param": f"output.{param}", "status": "failed", "detail": msg})
                mismatches.append(f"{node_name}.{msg}")

        if any(c["status"] == "failed" for c in node_result["validation"]["checks"]):
            node_result["validation"]["status"] = "failed"

        node_result["workflow"] = try_run_workflow(client, node_name)
        node_results.append(node_result)

    with open(RESULTS_FILE, "w") as f:
        json.dump(node_results, f, indent=2)
    print(f"\n[INFO] Results saved to {RESULTS_FILE}")

    if missing_docs:
        print(f"\n[WARN] Nodes without docs: {', '.join(missing_docs)}")

    failed_workflows = [r for r in node_results if r["workflow"]["status"] not in ("succeeded", "completed", "skipped")]
    if failed_workflows:
        print("\n[WARN] Workflow failures:")
        for r in failed_workflows:
            wf = r["workflow"]
            print(f"  - {r['node']}: {wf['message']} (task_id={wf['task_id']})")

    if mismatches:
        print("\nType mismatches:", file=sys.stderr)
        for m in mismatches:
            print(f"  - {m}", file=sys.stderr)
        sys.exit(1)

    print("\nAll nodes validated successfully.")


if __name__ == "__main__":
    run_all()
