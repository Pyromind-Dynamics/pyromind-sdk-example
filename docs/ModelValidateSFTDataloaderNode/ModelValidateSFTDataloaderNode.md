# Validate SFT Dataloader Node

![alt text](/imgs/ModelValidateSFTDataloaderNode/ModelValidateSFTDataloaderNode.png)  

## 1.1 Overview

Validate SFT dataloader configuration and collator entry.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| dataset_config | STRING | Yes | String value. Default: - |
| check_reasoning | BOOLEAN | No | Boolean flag (true/false). Default: `False` |
| limit | INT | No | Integer value. Default: `0` |
| verbose | BOOLEAN | No | Boolean flag (true/false). Default: `False` |
| preview_html_path | STRING | No | String value. Default: - |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| metrics_yaml | STRING | String value |
| output_preview_path | STRING | String value |

## 1.4 Workflow JSON Definition

See [`workflow/ModelValidateSFTDataloaderNode/ModelValidateSFTDataloaderNode.json`](../../workflow/ModelValidateSFTDataloaderNode/ModelValidateSFTDataloaderNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelValidateSFTDataloaderNode/ModelValidateSFTDataloaderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `modelValidateSFTDataloaderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
