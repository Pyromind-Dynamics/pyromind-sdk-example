# GRPO Training Node

![alt text](/imgs/ModelTrainGRPONode/ModelTrainGRPONode.png)

## 1.1 Overview

GRPO training aligned with SFT-style YAML: dataset_config, training_config (shared with SFT), grpo_extra_config (GRPO-only), model_config, reward_config. Returns output directory.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| output_path | STRING | Yes | Output directory or file path |
| dataset_config | STRING | Yes | Assembled dataset configuration YAML string |
| training_config | STRING | Yes | Training config YAML string (`BaseTrainingConfig` fields) |
| grpo_extra_config | STRING | No | GRPO-only extra training config YAML. Default: empty string |
| model_config | STRING | Yes | Model config YAML string |
| lora_config | STRING | No | LoRA config YAML string from Lora Config Builder |
| reward_config | STRING | Yes | Reward config YAML from Reward Config Builder |
| wandb_config | WANDB_CONFIG | No | W&B configuration object |
| thinking_as_input_ratio | FLOAT | No | Ratio of chain-of-thought content included as input. Default: `0.0` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| model_output_path | STRING | Trained model output directory |

## 1.4 Workflow JSON Definition

See [`workflow/ModelTrainGRPONode/ModelTrainGRPONode.json`](../../workflow/ModelTrainGRPONode/ModelTrainGRPONode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelTrainGRPONode/ModelTrainGRPONode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `modelTrainGRPONode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
