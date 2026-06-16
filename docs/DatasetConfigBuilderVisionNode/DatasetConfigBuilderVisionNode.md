# Dataset Kind Config Builder (Vision)

![alt text](/imgs/DatasetConfigBuilderVisionNode/DatasetConfigBuilderVisionNode.png)

## 1.1 Overview

Builds the `dataset_kind_config` YAML fragment for vision datasets (image + text fields). Connect its output to `DatasetConfigBuilderNode.dataset_kind_config`.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| system_prompt_field | STRING | No | System prompt field name. Default: empty string |
| user_prompt_field | STRING | No | User prompt field name. Default: empty string |
| image_field | STRING | Yes | Image field name |
| assistant_response_field | STRING | No | Assistant response / ground-truth field name. Default: `gt` |
| rejected_field | STRING | No | Rejected response / messages field name. Default: `rejected_answer` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| dataset_kind_config | STRING | Dataset kind config YAML from a Kind Config Builder node |

## 1.4 Workflow JSON Definition

See [`workflow/DatasetConfigBuilderVisionNode/DatasetConfigBuilderVisionNode.json`](../../workflow/DatasetConfigBuilderVisionNode/DatasetConfigBuilderVisionNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DatasetConfigBuilderVisionNode/DatasetConfigBuilderVisionNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `datasetConfigBuilderVisionNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
