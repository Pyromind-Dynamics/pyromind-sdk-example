# Training Config Builder Node

![alt text](/imgs/TrainingConfigBuilderNode/TrainingConfigBuilderNode.png)

## 1.1 Overview

Assembles shared SFT/GRPO/DPO training hyperparameters into a `training_config` YAML string.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| num_epochs | FLOAT | No | Default: `2` |
| batch_size | INT | No | Default: `2` |
| grad_accum | INT | No | Default: `2` |
| learning_rate | FLOAT | No | Default: `0.0001` |
| lr_scheduler_type | STRING | No | Default: `constant`. Options: linear, cosine, cosine_with_restarts, polynomial, constant, constant_with_warmup |
| logging_steps | INT | No | Default: `5` |
| save_steps | INT | No | Default: `500` |
| save_total_limit | INT | No | Default: `3` |
| eval_steps | INT | No | Default: `500` |
| seed | INT | No | Default: `42` |
| resume_from_checkpoint | STRING | No | Default: `''` |
| max_grad_norm | FLOAT | No | Default: `2` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| training_config | STRING | Built training configuration YAML string |

## 1.4 Workflow JSON Definition

See [`workflow/TrainingConfigBuilderNode/TrainingConfigBuilderNode.json`](../../workflow/TrainingConfigBuilderNode/TrainingConfigBuilderNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/TrainingConfigBuilderNode/TrainingConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `trainingConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
