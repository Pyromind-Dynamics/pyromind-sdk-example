# Reward Item Builder Node

![alt text](/imgs/RewardItemBuilder/RewardItemBuilder.png)  

## 1.1 Overview

Build a single reward item as YAML (entry, name, kwargs, weight). Non-empty kwargs implies factory=true; empty kwargs implies factory=false. 

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| entry | STRING | No | Reward function entry point path, e.g., `train.reward_fn:my_reward`. Must be non-empty at runtime, otherwise raises ValueError. Default: `''` |
| name | STRING | No | Optional name identifier for the reward item. Default: `''` |
| kwargs | STRING | No | YAML mapping string of keyword arguments passed to the reward function. Non-empty enables factory mode. Default: `''` |
| weight | FLOAT | No | Weight multiplier for this reward item in the combined reward score. Default: `1.0` |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| reward_item | STRING | YAML-formatted string representing the configured reward item. Contains fields: `entry`, `source` (fixed to `python_path`), `weight`, `factory`, `kwargs`, and optionally `name`. Passable to downstream reward configuration nodes. |

## 1.4 Workflow JSON Definition

See [`workflow/RewardItemBuilder/RewardItemBuilder.json`](../../workflow/RewardItemBuilder/RewardItemBuilder.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/RewardItemBuilder/RewardItemBuilder.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `rewardItemBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |

```bash
python -m pyromind_sdk.test_run_workflow_cli workflow/RewardItemBuilder/RewardItemBuilder.json  --pretty
```

Example output:

```json
{
  "task_id": "4878",
  "task_name": "rewarditembuildertest",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 18888,
      "node_type": "RewardItemBuilderNode",
      "label": "",
      "start_at": "2026-06-09 03:25:37",
      "end_at": "2026-06-09 03:25:51",
      "duration": "0:00:14",
      "input": {
        "entry": "/workspace/py/example_valid_node.py",
        "name": "example_valid_node",
        "kwargs": "",
        "weight": 1
      },
      "output": {
        "reward_item": "entry: /workspace/py/example_valid_node.py\nsource: python_path\nweight: 1.0\nfactory: false\nkwargs: {}\nname: example_valid_node"
      },
      "raw": {}
    }
  ]
}
```
