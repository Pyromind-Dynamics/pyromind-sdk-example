# PyroMind SDK Example

Python example project for the [PyroMind SDK](https://github.com/PyroMind-Dynamics/pyromind-sdk).

Provides an automated testing framework to verify SDK node behavior against documentation.

## Directory Structure

```
├── docs/          # Node definitions, I/O specs, and command examples
├── workflow/      # Workflow definition files
├── imgs/          # Flow charts, architecture diagrams, etc.
├── tests/         # Automated test suite (pytest)
└── main.py        # CLI: run workflow JSON, wait, export node I/O
```

## CLI (`main.py`)

Submit a workflow JSON file, wait for completion, and export each node's input and output.

```bash
python main.py <workflow.json> [options]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `workflow` | Path to workflow JSON file (required) |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | workflow file name | Task name |
| `--output` | `tests/test_output/<name>_result.json` | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |

### Examples

```bash
# Basic usage
python main.py workflow/LoadImage/LoadImage.json --pretty

# Custom name and output path
python main.py workflow/LoadDataset/LoadDataset.json --name my-test --output result.json --pretty

# Adjust polling
python main.py workflow/LoadImage/LoadImage.json --poll-interval 3 --timeout 300
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


