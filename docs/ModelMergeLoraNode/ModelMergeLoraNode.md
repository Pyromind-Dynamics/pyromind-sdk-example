# Merge LoRA Node

![alt text](/imgs/ModelMergeLoraNode/ModelMergeLoraNode.png)

## 1.1 Overview

Merge LoRA adapter into base weights (PEFT merge_and_unload) and save model + processor
to a standalone directory. Base model id/path may be omitted if adapter_config.json
contains base_model_name_or_path.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| lora_path | STRING | Yes | LoRA adapter directory path |
| output_path | STRING | Yes | Output directory path |
| model_path | STRING | Yes | Base model path or HuggingFace model ID. Default: `''` |
| model_type | STRING | No | Default: `auto`. Options: auto, qwen3vl, qwen3.5 |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| merged_model_path | STRING | Merged model output directory path |

## 1.4 Workflow JSON Definition

See [`workflow/ModelMergeLoraNode/ModelMergeLoraNode.json`](../../workflow/ModelMergeLoraNode/ModelMergeLoraNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelMergeLoraNode/ModelMergeLoraNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `modelMergeLoraNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
