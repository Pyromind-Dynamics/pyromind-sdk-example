# Reward Item Builder(Custom Entry) Node

![alt text](/imgs/RewardItemBuilderCustomNode/RewardItemBuilderCustomNode.png)

## 1.1 Overview

Build a single reward item as YAML (entry, name, kwargs, weight). Non-empty kwargs implies factory=true; empty kwargs implies factory=false.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| entry | STRING | Yes | Default: `''` |
| name | STRING | Yes | Default: `''` |
| kwargs | STRING | No | Default: `''` |
| weight | FLOAT | No | Default: `1.0` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| reward_item | STRING | Built reward item YAML string |

## 1.4 Workflow JSON Definition

See [`workflow/RewardItemBuilderCustomNode/RewardItemBuilderCustomNode.json`](../../workflow/RewardItemBuilderCustomNode/RewardItemBuilderCustomNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/RewardItemBuilderCustomNode/RewardItemBuilderCustomNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `rewardItemBuilderCustomNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
