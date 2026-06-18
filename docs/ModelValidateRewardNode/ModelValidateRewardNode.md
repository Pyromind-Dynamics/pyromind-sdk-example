# Validate Reward Node

![alt text](/imgs/ModelValidateRewardNode/ModelValidateRewardNode.png)

## 1.1 Overview

Validate reward composition and score aggregation.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| reward_config | STRING | Yes | Reward configuration YAML string |
| completions | STRING | No | Default: `''` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| status | STRING | status |
| scores | STRING | scores |

## 1.4 Workflow JSON Definition

See [`workflow/ModelValidateRewardNode/ModelValidateRewardNode.json`](../../workflow/ModelValidateRewardNode/ModelValidateRewardNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelValidateRewardNode/ModelValidateRewardNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `modelValidateRewardNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
