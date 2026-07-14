# Dataset Kind Config Builder (Messages)

![alt text](/imgs/DatasetConfigBuilderMessageNode/DatasetConfigBuilderMessageNode.png)

## 1.1 Overview

Builds the `dataset_kind_config` YAML fragment for chat/messages datasets. Connect its output to `DatasetConfigBuilderNode.dataset_kind_config`.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| messages_field | STRING | Yes | Messages field name |
| rejected_field | STRING | No | Rejected response / messages field name. Default: `rejected_messages` |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| dataset_kind_config | STRING\|DATASET_KIND_CONFIG | Dataset kind config YAML from a Kind Config Builder node |
## 1.4 Workflow JSON Definition

See [`workflow/DatasetConfigBuilderMessageNode/DatasetConfigBuilderMessageNode.json`](../../workflow/DatasetConfigBuilderMessageNode/DatasetConfigBuilderMessageNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DatasetConfigBuilderMessageNode/DatasetConfigBuilderMessageNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `datasetConfigBuilderMessageNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
