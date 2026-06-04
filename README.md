# PyroMind SDK Example

Python example project for the [PyroMind SDK](https://github.com/PyroMind-Dynamics/pyromind-sdk).

Provides an automated testing framework to verify SDK node behavior against documentation.

## Directory Structure

```
├── docs/              # Node definitions, I/O specs, and command examples
├── workflow/          # Workflow definition files
├── imgs/              # Flow charts, architecture diagrams, etc.
├── tests/             # Automated test suite
│   ├── test_workflow.py   # Run workflow JSON, wait, export node I/O
│   ├── test_single_node.py
│   └── test_node_doc_consistency.py
```

## Workflow Test (`test_workflow.py`)

Submit a workflow JSON file via the SDK, wait for completion, and export each node's input and output.

```bash
export PYROMIND_API_KEY=<your-api-key>
python tests/test_workflow.py <workflow.json>
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `workflow.json` | `workflow/LoadDataset/LoadDataset.json` | Path to workflow JSON file (relative to project root) |

### Examples

```bash
# Run LoadDataset workflow
python tests/test_workflow.py workflow/LoadDataset/LoadDataset.json

# Run LoadImage workflow
python tests/test_workflow.py workflow/LoadImage/LoadImage.json
```

Results are saved to `tests/test_output/<name>_result.json`.

## Test Modes (`tests/`)

The test framework is document-driven and supports two modes:

### 1. Full Node Validation

Read all system nodes via the SDK, then automatically compare each node's input/output against the definitions in `docs/`, and run their workflows.

### 2. Single / Specific Node Test

Use `test_single_node.py` with `--node` filter or `PYROMIND_NODES` env var to test specific nodes in isolation for quick troubleshooting.

## SDK

This project depends on the [PyroMind SDK](https://github.com/PyroMind-Dynamics/pyromind-sdk).

## Setup

```bash
pip install pyromind-sdk
```

Set the required environment variables:

```bash
export PYROMIND_API_KEY=<your-api-key>
export PYROMIND_BASE_URL=https://api-portal.pyromind.ai/api/v1
export PYROMIND_CLUSTER=us-west-2
```

## Running Tests

```bash
# Full node validation — compare all system nodes against docs
python tests/test_node_doc_consistency.py

# Single / specific node tests
python tests/test_single_node.py --node LoadImage
python tests/test_single_node.py --node "LoadImage or LoadDataset"

# Or via environment variable
PYROMIND_NODES="LoadImage" python tests/test_single_node.py
```


