# Dataset Config Builder Node

![alt text](/imgs/DatasetConfigBuilderNode/DatasetConfigBuilderNode.png)

## 1.1 Overview

Builds a dataset configuration YAML string for SFT/GRPO/DPO training. Combines `train_data_path`, optional `dataset_kind_config` (from Vision/Text/Messages builders), and optional `dataset_extra_config` (from Dataset Extra Config Builder).

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| train_data_path | STRING | Yes | Training data path |
| val_data_path | STRING | No | Validation data path. Default: `''` |
| dataset_kind_config | STRING | No | Kind config YAML from Vision/Text/Messages builder. Default: `''` |
| dataset_extra_config | STRING | No | Extra config YAML from Dataset Extra Config Builder. Default: `''` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| dataset_config | STRING | Built dataset configuration YAML string |

## 1.4 Workflow JSON Definition

See [`workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json`](../../workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json) for the full workflow definition.

Example configuration (typical pipeline: Vision Kind Builder → Extra Config Builder → Dataset Config Builder):
```json
{
  "config": {
    "train_data_path": "/workspace/datasets/openai/gsm8k/train.jsonl",
    "val_data_path": "",
    "dataset_kind_config": "dataloader_kind: vision\nimage_field: image_path\nassistant_response_field: gt",
    "dataset_extra_config": "max_seq_length: 4096\nsft_collator_entry: train.sft_collator:make_collate_fn"
  }
}
```

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `DatasetConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
