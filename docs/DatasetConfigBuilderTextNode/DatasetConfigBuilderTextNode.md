# Dataset Kind Config Builder (Text Only)

![alt text](/imgs/DatasetConfigBuilderTextNode/DatasetConfigBuilderTextNode.png)

## 1.1 Overview

Builds the `dataset_kind_config` YAML fragment for text-only datasets. Connect its output to `DatasetConfigBuilderNode.dataset_kind_config`.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| system_prompt_field | STRING | No | System prompt field name. Default: empty string |
| user_prompt_field | STRING | No | User prompt field name. Default: empty string |
| assistant_response_field | STRING | No | Assistant response / ground-truth field name. Default: `gt` |
| rejected_field | STRING | No | Rejected response / messages field name. Default: `rejected_answer` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| dataset_kind_config | STRING | Dataset kind config YAML from a Kind Config Builder node |

## 1.4 Workflow JSON Definition

See [`workflow/DatasetConfigBuilderTextNode/DatasetConfigBuilderTextNode.json`](../../workflow/DatasetConfigBuilderTextNode/DatasetConfigBuilderTextNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DatasetConfigBuilderTextNode/DatasetConfigBuilderTextNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `datasetConfigBuilderTextNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
