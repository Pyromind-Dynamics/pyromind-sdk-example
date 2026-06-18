# Wandb Config Builder Node

![alt text](/imgs/WandbConfigBuilderNode/WandbConfigBuilderNode.png)

## 1.1 Overview

Build wandb_config YAML string for W&B training runtime env.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| wandb_api_key | STRING | Yes | W&B API key. Default: `''` |
| wandb_project | STRING | Yes | W&B project name. Default: `''` |
| wandb_name | STRING | No | W&B run name. Default: `''` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| wandb_config | WANDB_CONFIG | W&B configuration YAML |

## 1.4 Workflow JSON Definition

See [`workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json`](../../workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json) for the full workflow definition.

Example configuration:
```json
{
  "config": {
    "wandb_api_key": "",
    "wandb_project": "test-01",
    "wandb_name": "run-001"
  }
}
```

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `wandbConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |

```bash
python -m pyromind_sdk.test_run_workflow_cli workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json --pretty
```

Example output:

```json
{
  "task_id": "4922",
  "task_name": "wandb",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 18988,
      "node_type": "WandbConfigBuilderNode",
      "label": "",
      "start_at": "2026-06-09 09:33:15",
      "end_at": "2026-06-09 09:33:32",
      "duration": "0:00:17",
      "input": {
        "wandb_api_key": "",
        "wandb_project": "test-01",
        "wandb_name": "run-001"
      },
      "output": {
        "wandb_config": "WANDB_PROJECT: test-01\nWANDB_NAME: run-001"
      },
      "raw": {}
    }
  ]
}
```
