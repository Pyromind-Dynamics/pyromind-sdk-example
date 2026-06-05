# Dataset Config Builder Node

![alt text](/imgs/DatasetConfigBuilderNode/DatasetConfigBuilderNode.png)  

## {{section}} Overview

Build dataset config YAML string for SFT/GRPO.

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| train_data_path | STRING | Yes | String value. Default: - |
| val_data_path | STRING | No | String value. Default: - |
| dataloader_kind | STRING | No | String value. Default: `vision` |
| image_field | STRING | No | String value. Default: `image_path` |
| assistant_response_field | STRING | No | String value. Default: `gt` |
| rejected_field | STRING | No | String value. Default: - |
| messages_field | STRING | No | String value. Default: `messages` |
| user_prompt_field | STRING | No | String value. Default: - |
| system_prompt_field | STRING | No | String value. Default: - |
| sft_collator_entry | STRING | No | String value. Default: `train.sft_collator:make_collate_fn` |
| dpo_collator_entry | STRING | No | String value. Default: - |
| grpo_collator_entry | STRING | No | String value. Default: - |
| max_seq_length | INT | No | Integer value. Default: `4096` |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| dataset_config | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json`](../../workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json) for the full workflow definition.

## {{section}} Running the Workflow

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
