# PyroMind SDK Example

Python example project for the [PyroMind SDK](https://github.com/PyroMind-Dynamics/pyromind-sdk).

Provides an automated testing framework to verify SDK node behavior against documentation.

## Directory Structure

```
├── docs/          # Node definitions, I/O specs, and command examples
├── workflow/      # Workflow definition files
├── imgs/          # Flow charts, architecture diagrams, etc.
├── tests/         # Automated test suite (pytest)
└── main.py        # Entry point
```

## Test Modes (`tests/`)

The test framework is document-driven and supports three modes:

### 1. Full Node Validation

Pass an `sk` (API Key) to read all system nodes via the SDK, then automatically compare each node's input/output against the definitions in `docs/`.

### 2. Single / Specific Node Test

Use `test_single_node.py` with `-k` filter or `PYROMIND_NODES` env var to test specific nodes in isolation for quick troubleshooting.

### 3. Command Parsing Test

Parse command definitions from `docs/`, invoke them via the SDK, and verify the results match expectations.

## SDK

This project depends on the [PyroMind SDK](https://github.com/PyroMind-Dynamics/pyromind-sdk).

## Setup

```bash
pip install pyromind-sdk
```

Set the required environment variables:

```bash
export PYROMIND_API_KEY=sk-your-api-key
export PYROMIND_BASE_URL=https://api-portal.pyromind.ai/api/v1
export PYROMIND_CLUSTER=us-west-2
```

## Running Tests

```bash
# Full node validation — compare all system nodes against docs
python tests/test_node_doc_consistency.py

# Single / specific node tests (pytest parameterized, use -k to filter)
pytest tests/test_single_node.py -k "LoadImage"
pytest tests/test_single_node.py -k "LoadImage or LoadDataset"

# Or via environment variable
PYROMIND_NODES="LoadImage" pytest tests/test_single_node.py
```

## Usage

```python
from pyromind_sdk import PyroMindAPIClient

client = PyroMindAPIClient()  # reads PYROMIND_API_KEY automatically

# Get all system nodes
nodes = client.studio.get_node_info()

# Run a workflow with a node
from pyromind_sdk.client.models import WorkflowRunRequest
resp = client.studio.run_with_params(WorkflowRunRequest(
    workflow_name="my_workflow",
    primitive_node_map={"dataset_path": "/path/to/data"}
))
```
