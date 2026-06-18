# GRPO Training Node

![alt text](/imgs/ModelTrainGRPONode/ModelTrainGRPONode.png)

## 1.1 Overview

Main GRPO training node using SFT-aligned YAML: dataset_config, training_config, grpo_extra_config, model_config, reward_config, and optional lora_config.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| output_path | STRING | Yes | Output directory path |
| dataset_config | STRING | Yes | Dataset configuration YAML string |
| training_config | STRING | Yes | Training configuration YAML string |
| model_config | STRING | Yes | Model configuration YAML string |
| grpo_extra_config | STRING | No | GRPO-only extra configuration YAML. Default: `''` |
| lora_config | STRING | No | LoRA configuration YAML string |
| reward_config | STRING | Yes | Reward configuration YAML string |
| wandb_config | WANDB_CONFIG | No | W&B configuration |
| thinking_as_input_ratio | FLOAT | No | Include chain-of-thought content as input at the given ratio. Default: `0.0` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| model_output_path | STRING | Trained model output directory path |

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
