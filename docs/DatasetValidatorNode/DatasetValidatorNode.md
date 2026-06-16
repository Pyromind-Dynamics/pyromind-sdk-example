# Dataset Validator

![alt text](/imgs/DatasetValidatorNode/DatasetValidatorNode.png)

## 1.1 Overview

Validates an assembled `dataset_config`, builds a dataloader preview, and outputs validation metrics plus an HTML preview path.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| dataset_config | STRING | Yes | Assembled dataset configuration YAML string |
| check_reasoning | BOOLEAN | No | Validate reasoning fields in the dataset. Default: false |
| limit | INT | No | Max samples for validation preview (0 = no limit). Default: `0` |
| verbose | BOOLEAN | No | Print detailed validation logs. Default: false |
| preview_html_path | STRING | No | HTML preview output path. Default: `/workspace/datasets/preview.html` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| metrics_yaml | STRING | Validation metrics as YAML string |
| output_preview_path | STRING | Generated HTML preview file path |

## 1.4 Workflow JSON Definition

See [`workflow/DatasetValidatorNode/DatasetValidatorNode.json`](../../workflow/DatasetValidatorNode/DatasetValidatorNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DatasetValidatorNode/DatasetValidatorNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `datasetValidatorNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
