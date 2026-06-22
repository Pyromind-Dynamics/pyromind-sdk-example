# Validate GRPO Dataloader Node

![alt text](/imgs/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.png)

## 1.1 Overview

Validate GRPO dataloader configuration, reward config, and rollout behavior.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| dataset_config | STRING | Yes | Assembled dataset configuration YAML string |
| rollout_size | INT | No | Rollout size. Default: `3` |
| check_reasoning | BOOLEAN | No | Validate reasoning fields in the dataset. Default: false |
| limit | INT | No | Max samples for validation preview (0 = no limit). Default: `0` |
| verbose | BOOLEAN | No | Print detailed validation logs. Default: false |
| preview_html_path | STRING | No | HTML preview output path. Default: empty string |
| reward_config | STRING | No | Reward config YAML from Reward Config Builder. Default: empty string |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| metrics_json | STRING | Validation metrics JSON string |
| output_preview_path | STRING | Generated HTML preview file path |

## 1.4 Workflow JSON Definition

See [`workflow/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.json`](../../workflow/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.json) for the full workflow definition.

## 1.5 Running the Workflow

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
