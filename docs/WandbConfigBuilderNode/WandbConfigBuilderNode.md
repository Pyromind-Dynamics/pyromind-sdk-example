# Wandb Config Builder Node

![alt text](/imgs/WandbConfigBuilderNode/WandbConfigBuilderNode.png)

## 1.1 Overview

Builds a `wandb_config` YAML string for W&B (Weights & Biases) training runtime environment. This node is used to configure W&B experiment tracking parameters, enabling recording and visualization of experiment metrics during training.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| wandb_api_key | STRING | No | W&B API key for authentication. Default: empty string |
| wandb_project | STRING | No | W&B project name for organizing experiments. Default: empty string |
| wandb_run_group | STRING | No | W&B run group name for grouping related experiments. Default: empty string |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| wandb_config | STRING | Built W&B configuration object for downstream training nodes |

## 1.4 Workflow JSON Definition

See [`workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json`](../../workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json) for the full workflow definition.

Example configuration:
```json
{
  "config": {
    "wandb_api_key": "",
    "wandb_project": "test-01",
    "wandb_run_group": "daskdas"
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
| `--name` | `WandbConfigBuilderNode` | Task name |
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
        "wandb_run_group": "daskdas"
      },
      "output": {
        "wandb_config": "WANDB_PROJECT: test-01\nWANDB_RUN_GROUP: daskdas"
      },
      "raw": {}
    }
  ]
}
```
