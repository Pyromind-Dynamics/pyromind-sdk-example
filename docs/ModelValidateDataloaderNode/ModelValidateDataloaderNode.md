# Validate Dataloader Node

![alt text](/imgs/ModelValidateDataloaderNode/ModelValidateDataloaderNode.png)  

## {{section}} Overview

Validate dataloader configuration and sample readability.

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| data_path | STRING | Yes | String value. Default: - |
| dataloader_kind | STRING | Yes | String value. Default: - |
| image_field | STRING | No | String value. Default: `image_path` |
| text_field | STRING | No | String value. Default: `text` |
| target_field | STRING | No | String value. Default: `text` |
| messages_field | STRING | No | String value. Default: `messages` |
| component_type_field | STRING | No | String value. Default: - |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| status | STRING | String value |
| metrics | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/ModelValidateDataloaderNode/ModelValidateDataloaderNode.json`](../../workflow/ModelValidateDataloaderNode/ModelValidateDataloaderNode.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelValidateDataloaderNode/ModelValidateDataloaderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `modelValidateDataloaderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
