# Validate Reward Node

![alt text](/imgs/ModelValidateRewardNode/ModelValidateRewardNode.png)  

## {{section}} Overview

Validate reward composition and score aggregation.

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| reward_items | STRING | Yes | String value. Default: - |
| normalize | BOOLEAN | No | Boolean flag (true/false). Default: `False` |
| completions | STRING | No | String value. Default: - |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| status | STRING | String value |
| scores | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/ModelValidateRewardNode/ModelValidateRewardNode.json`](../../workflow/ModelValidateRewardNode/ModelValidateRewardNode.json) for the full workflow definition.

## {{section}} Running the Workflow

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
