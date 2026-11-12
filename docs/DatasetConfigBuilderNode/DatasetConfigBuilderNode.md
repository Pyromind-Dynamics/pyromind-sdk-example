# Dataset Config Builder Node

![alt text](/imgs/DatasetConfigBuilderNode/DatasetConfigBuilderNode.png)

## 1.1 Overview

Builds the base `dataset_config` YAML string for SFT/GRPO/DPO training. Combine with a **Dataset Kind Config Builder** node (Vision / Text / Messages) and **Dataset Extra Config Builder** to supply `dataset_kind_config` and `dataset_extra_config` inputs.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| train_data_path | STRING\|PATH | Yes | Training data path |
| val_data_path | STRING\|PATH | No | Validation data path. Default: empty string |
| dataset_kind_config | STRING\|DATASET_KIND_CONFIG | No | Dataset kind config YAML from a Kind Config Builder node. Default: empty string |
| dataset_extra_config | STRING\|DATASET_EXTRA_CONFIG | No | Dataset extra config YAML from Dataset Extra Config Builder. Default: empty string |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| dataset_config | STRING\|DATASET_CONFIG | Assembled dataset configuration YAML string |
## 1.4 Workflow JSON Definition

See [`workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json`](../../workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `datasetConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
