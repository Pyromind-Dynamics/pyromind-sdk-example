# Reward Item Builder (System Entry)

![alt text](/imgs/RewardItemBuilderNode/RewardItemBuilderNode.png)

## 1.1 Overview

Builds a single reward item YAML using a built-in reward entry. Non-empty `kwargs` enables factory mode.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| entry | STRING | Yes | Built-in reward function name. Options: `geometry_vqa_thinking_reward`, `geometry_vqa_answer_reward`. Default: `geometry_vqa_thinking_reward` |
| name | STRING | Yes | Metric or reward item name |
| kwargs | STRING | No | YAML mapping of keyword arguments (non-empty enables factory mode). Default: empty string |
| weight | FLOAT | No | Weight multiplier in combined score. Default: `1.0` |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| reward_item | STRING\|REWARD_ITEM | Single reward item YAML string |
## 1.4 Workflow JSON Definition

See [`workflow/RewardItemBuilderNode/RewardItemBuilderNode.json`](../../workflow/RewardItemBuilderNode/RewardItemBuilderNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/RewardItemBuilderNode/RewardItemBuilderNode.json [options]
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
