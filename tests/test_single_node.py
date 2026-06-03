"""Validate and run workflows for specific nodes (use -k to filter)."""

import json
import os
import re
import time
from pathlib import Path

import pytest
from pyromind_sdk.client.models import TrainingTaskCreateRequest

from pyromind_sdk import PyroMindAPIClient

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
        resp = client.studio.create(TrainingTaskCreateRequest(
            name=f"test_{node_name}",
            workflow=workflow_data,
        ))
        if not resp or not resp.task_id:
            result["status"] = "error"
            result["message"] = "create task returned no task_id"
            return result
    except Exception as e:
        err_msg = str(e)
        if "not found" in err_msg.lower():
            return result
        result["status"] = "error"
        result["message"] = f"workflow create failed — {e}"
        return result

    task_id = resp.task_id
    result["task_id"] = task_id
    poll_interval = 3
    timeout = 300
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            job = client.studio.get_job(task_id)
            status = getattr(job, "status", "").lower()
            result["status"] = status
            if status in ("completed", "succeeded"):
                result["message"] = "workflow succeeded"
                return result
            if status in ("failed", "error", "cancelled", "stopped"):
                result["message"] = f"workflow ended with status={status}"
                return result
            if status in ("running", "pending", ""):
                time.sleep(poll_interval)
                continue
        except Exception as e:
            result["status"] = "error"
            result["message"] = f"poll task {task_id} failed — {e}"
            return result

    result["status"] = "timeout"
    result["message"] = f"timed out after {timeout}s"
    return result


def get_nodes() -> list[str]:
    env_nodes = os.environ.get("PYROMIND_NODES")
    if env_nodes:
        return [n.strip() for n in env_nodes.split(",") if n.strip()]
    return NODES


@pytest.fixture(scope="session")
def client():
    return PyroMindAPIClient()


@pytest.fixture(scope="session")
def sdk_nodes(client):
    return client.studio.get_node_info()


@pytest.mark.parametrize("node_name", get_nodes())
def test_single_node(node_name, client, sdk_nodes):
    assert isinstance(sdk_nodes, dict), f"Expected dict, got {type(sdk_nodes)}"

    info = sdk_nodes.get(node_name)
    assert info is not None, f"Node '{node_name}' not found in SDK"

    spec = extract_node_spec_from_docs(node_name)
    mismatches = []

    if spec is None:
        pytest.skip(f"No docs for node '{node_name}'")

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
        pytest.fail(f"Type mismatches for '{node_name}':\n" + "\n".join(f"  - {m}" for m in mismatches))

    # run workflow
    wf_result = try_run_workflow(client, node_name)

    # append to results file
    results = []
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE) as f:
            results = json.load(f)
    results.append({"node": node_name, "validation": "passed", "workflow": wf_result})
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
