# GRPO Training Node

![alt text](/imgs/ModelTrainGRPONode/ModelTrainGRPONode.png)  

## 1.1 Overview

GRPO training aligned with SFT-style YAML: dataset_config, training_config (shared with SFT),
grpo_extra_config (GRPO-only), model_config, reward_config. Returns output directory.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| output_path | STRING | Yes | String value. Default: - |
| dataset_config | STRING | Yes | String value. Default: - |
| training_config | STRING | Yes | String value. Default: - |
| model_config | STRING | Yes | String value. Default: - |
| reward_config | STRING | Yes | String value. Default: - |
| accelerate_config | ACCELERATE_CONFIG | Yes | Accelerate configuration YAML. Default: - |
| gpu_count | INT | Yes | Integer value. Default: `1` |
| gpu_product | STRING | Yes | String value. Default: `NVIDIA-H100-NVL` Options: NVIDIA-H100-NVL, NVIDIA-L40S, NVIDIA-H200, NVIDIA-B200, NVIDIA-H100-80GB-HBM3 |
| grpo_extra_config | STRING | No | String value. Default: - |
| wandb_config | WANDB_CONFIG | No | W&B configuration YAML. Default: - |
| thinking_as_input_ratio | FLOAT | No | Floating point number. Default: `0.0` |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| model_output_path | STRING | String value |

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
