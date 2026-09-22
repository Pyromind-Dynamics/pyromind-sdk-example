#!/usr/bin/env python3
"""Create sanitized, single-node workflow examples for documented API nodes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pyromind_sdk import PyroMindAPIClient


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / "workflow"

MISSING_NODES = (
    "ContentPreview",
    "CustomCommandNode",
    "DataPreprocessLabelNode",
    "DataPreprocessMergeNode",
    "DataPreprocessPromptExpandNode",
    "DataPreprocessReasoningNode",
    "DatasetConfigBuilderVisionNode",
    "DatasetValidatorNode",
    "MetricsConfigBuilderCustomNode",
    "MetricsConfigBuilderNode",
    "ModelEvalApiNode",
    "ModelTrainGRPONode",
    "ModelTrainOPDNode",
    "ModelValidateGRPODataloaderNode",
    "ModelValidateRewardNode",
    "PreviewFile",
    "PreviewImageEx",
    "PythonFileProcessorNode",
    "RewardItemBuilderCustomNode",
)

FALLBACK_DEFINITIONS = {
    "CustomCommandNode": {
        "input": {
            "required": {
                "command": ["STRING", {"default": "echo hello from custom command"}],
                "cpu": ["INT", {"default": 4, "min": 1, "max": 64}],
                "memory": ["INT", {"default": 32, "min": 1, "max": 256}],
                "gpu_count": ["INT", {"default": 0, "min": 0, "max": 8}],
                "gpu_product": [
                    "STRING",
                    {
                        "default": "NVIDIA-L40S",
                        "enum": [
                            "NVIDIA-H100-NVL",
                            "NVIDIA-H200",
                            "NVIDIA-H100-80GB-HBM3",
                            "NVIDIA-L40S",
                        ],
                    },
                ],
            },
            "optional": {},
        },
        "output": ["STRING"],
        "output_is_list": [False],
        "output_name": ["result"],
        "category": "utils",
        "description": "Run a custom shell command with configurable CPU and GPU resources.",
    },
    "PythonFileProcessorNode": {
        "input": {
            "required": {
                "file_path": ["STRING", {"default": ""}],
                "output_file_path": ["STRING", {"default": "/workspace/output.json"}],
                "python_script_path": ["STRING", {"default": ""}],
                "overwrite_output": ["BOOLEAN", {"default": False}],
            },
            "optional": {},
        },
        "output": ["STRING"],
        "output_is_list": [False],
        "output_name": ["output_file_path"],
        "category": "utils",
        "description": "Run a Python file processor and return the output file path.",
    },
}


def default_value(spec: object) -> object:
    dtype = spec[0] if isinstance(spec, list) and spec else spec
    config = spec[1] if isinstance(spec, list) and len(spec) > 1 and isinstance(spec[1], dict) else {}
    if "default" in config:
        return config["default"]
    if dtype == "BOOLEAN":
        return False
    if dtype in {"INT", "FLOAT"}:
        return 0
    if dtype == "ENV":
        return {}
    return ""


def build_workflow(node_name: str, definition: dict) -> dict:
    config = {}
    for group in ("required", "optional"):
        for name, spec in definition.get("input", {}).get(group, {}).items():
            config[name] = default_value(spec)

    node_data = {
        "nodeType": node_name,
        "nodeDefinition": definition,
        "config": config,
        "definitionMissing": False,
        "display_name": definition.get("display_name") or node_name,
        "libraryNodeId": str(definition.get("id", "")),
        "width": 300,
    }
    return {
        "id": str(uuid4()),
        "name": f"{node_name} example",
        "nodes": [{
            "id": "1",
            "type": "default",
            "position": {"x": 0, "y": 0},
            "data": node_data,
            "style": {"width": 300},
            "properties": {},
        }],
        "edges": [],
        "viewport": {"x": 0, "y": 0, "zoom": 1},
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def main() -> None:
    api_nodes = PyroMindAPIClient().studio.get_node_info()
    for node_name in MISSING_NODES:
        definition = api_nodes[node_name]
        if not definition.get("input") and node_name in FALLBACK_DEFINITIONS:
            definition = {**definition, **FALLBACK_DEFINITIONS[node_name]}
        output_path = WORKFLOW_DIR / node_name / f"{node_name}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(build_workflow(node_name, definition), indent=2) + "\n")
        print(f"Wrote {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
