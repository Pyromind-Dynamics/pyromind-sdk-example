# PyroMind SDK Example

Python examples and documentation for [PyroMind SDK](https://github.com/PyroMind-Dynamics/pyromind-sdk) nodes. The repository keeps English and Chinese node pages, UI screenshots, and example workflows together so their inputs and outputs can be checked against the node definitions.

## Repository layout

| Path | Contents |
|------|----------|
| `docs/<NodeName>/` | English node documentation |
| `docs_zh/<NodeName>/` | Chinese node documentation |
| `imgs/<NodeName>/` | Node UI screenshots referenced by both pages |
| `workflow/<NodeName>/` | Example workflow JSON |
| `nodes/` | Local custom-node and plugin examples; see [nodes/README.md](nodes/README.md) |
| `tests/` | Node definition checks and optional workflow runs |

## Setup

Requires Python 3.10 or newer. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

The documentation is maintained against `us-west-2#pre`. Set the API key locally and select that cluster and its API URL explicitly when checking or running these examples:

```bash
export PYROMIND_API_KEY=<your-api-key>
export PYROMIND_CLUSTER='us-west-2#pre'
export PYROMIND_BASE_URL='https://pre-api-us-west-2.pyromind.ai/api/v1/'
```

If you target another environment, set both `PYROMIND_CLUSTER` and `PYROMIND_BASE_URL` for that environment. Its node definitions and available GPUs may differ from the pages here.

## Check node documentation

The asset audit checks that each known node has both language pages, a workflow, and a screenshot:

```bash
python skills/pyromind-node-maintainer/scripts/audit_node_assets.py --repo .
```

`nodes/CustomNode.yaml` is a local sample and intentionally has no page, workflow, or screenshot; the audit lists those four gaps. With a valid API key, check documented input types, required flags, and missing input rows against the target cluster:

```bash
python skills/pyromind-node-maintainer/scripts/sync_node_doc_types.py \
  --repo . --cluster "$PYROMIND_CLUSTER" \
  --base-url "$PYROMIND_BASE_URL" --check
```

## Run a workflow

The SDK CLI submits a workflow, waits for completion, and can export each node's inputs and outputs. For example:

```bash
python -m pyromind_sdk.test_run_workflow_cli workflow/LoadImage/LoadImage.json --pretty
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | From JSON | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Maximum wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Maximum API request retries |
| `-h, --help` | - | Show help |

`tests/test_node_doc_consistency.py --validate-only` compares English doc types with the SDK without running workflows. Omitting `--validate-only` also submits every available example workflow:

```bash
python tests/test_node_doc_consistency.py --validate-only
```

`tests/test_single_node.py` runs the selected workflow after checking its English doc types. Its built-in node list contains `LoadImage` and `LoadDataset`; set `PYROMIND_NODES` to select another documented node:

```bash
python tests/test_single_node.py --node LoadImage
PYROMIND_NODES=PythonFileProcessorNode python tests/test_single_node.py --node PythonFileProcessorNode
```
