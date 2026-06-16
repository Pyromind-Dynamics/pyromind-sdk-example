# Dataset to JSONL Node

![alt text](/imgs/DatasetToJsonlNode/DatasetToJsonlNode.png)

## 1.1 Overview

Converts a HuggingFace dataset directory to a JSONL file path.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| dataset_path | STRING | Yes | Input dataset directory path |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| jsonl_path | STRING | Output JSONL file path |

## 1.4 Workflow JSON Definition

See [`workflow/DatasetToJsonlNode/DatasetToJsonlNode.json`](../../workflow/DatasetToJsonlNode/DatasetToJsonlNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DatasetToJsonlNode/DatasetToJsonlNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `datasetToJsonlNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
