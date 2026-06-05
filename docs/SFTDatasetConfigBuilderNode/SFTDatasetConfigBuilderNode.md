# SFT Dataset Config Builder Node

![alt text](/imgs/SFTDatasetConfigBuilderNode/SFTDatasetConfigBuilderNode.png)  

## 1.1 Overview

Build SFT dataset config YAML string.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| train_data_path | STRING | Yes | String value. Default: - |
| val_data_path | STRING | No | String value. Default: - |
| dataloader_kind | STRING | No | String value. Default: `vision` |
| image_field | STRING | No | String value. Default: `image_path` |
| text_field | STRING | No | String value. Default: `text` |
| messages_field | STRING | No | String value. Default: `messages` |
| user_prompt_field | STRING | No | String value. Default: - |
| system_prompt_field | STRING | No | String value. Default: - |
| collator_entry | STRING | No | String value. Default: `train.sft_collator:make_collate_fn` |
| max_seq_length | INT | No | Integer value. Default: `4096` |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| dataset_config | STRING | String value |

## 1.4 Workflow JSON Definition

See [`workflow/SFTDatasetConfigBuilderNode/SFTDatasetConfigBuilderNode.json`](../../workflow/SFTDatasetConfigBuilderNode/SFTDatasetConfigBuilderNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/SFTDatasetConfigBuilderNode/SFTDatasetConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `sFTDatasetConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
