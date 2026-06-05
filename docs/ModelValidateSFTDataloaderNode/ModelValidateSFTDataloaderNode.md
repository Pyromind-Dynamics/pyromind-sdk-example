# Validate SFT Dataloader Node

![alt text](/imgs/ModelValidateSFTDataloaderNode/ModelValidateSFTDataloaderNode.png)  

## {{section}} Overview

Validate SFT dataloader configuration and collator entry.

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| dataset_config | STRING | Yes | String value. Default: - |
| check_reasoning | BOOLEAN | No | Boolean flag (true/false). Default: `False` |
| limit | INT | No | Integer value. Default: `0` |
| verbose | BOOLEAN | No | Boolean flag (true/false). Default: `False` |
| preview_html_path | STRING | No | String value. Default: - |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| metrics_yaml | STRING | String value |
| output_preview_path | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/ModelValidateSFTDataloaderNode/ModelValidateSFTDataloaderNode.json`](../../workflow/ModelValidateSFTDataloaderNode/ModelValidateSFTDataloaderNode.json) for the full workflow definition.

## {{section}} Running the Workflow

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
