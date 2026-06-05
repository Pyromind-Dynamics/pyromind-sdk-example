# Validate GRPO Dataloader Node

![alt text](/imgs/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.png)  

## {{section}} Overview

Validate GRPO dataloader configuration, reward config, and rollout behavior.

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| dataset_config | STRING | Yes | String value. Default: - |
| rollout_size | INT | No | Integer value. Default: `3` |
| check_reasoning | BOOLEAN | No | Boolean flag (true/false). Default: `False` |
| limit | INT | No | Integer value. Default: `0` |
| verbose | BOOLEAN | No | Boolean flag (true/false). Default: `False` |
| preview_html_path | STRING | No | String value. Default: - |
| reward_config | STRING | No | String value. Default: - |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| metrics_json | STRING | String value |
| output_preview_path | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.json`](../../workflow/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `modelValidateGRPODataloaderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
