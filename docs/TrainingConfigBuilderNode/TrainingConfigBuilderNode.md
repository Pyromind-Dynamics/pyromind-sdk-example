# Training Config Builder Node

![alt text](/imgs/TrainingConfigBuilderNode/TrainingConfigBuilderNode.png)

## 1.1 Overview

Assembles shared SFT/GRPO/DPO training hyperparameters into a `training_config` YAML string for downstream training nodes.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| num_epochs | FLOAT | No | Number of training epochs. Default: `2` |
| batch_size | INT | No | Per-device batch size. Default: `2` |
| grad_accum | INT | No | Gradient accumulation steps. Default: `2` |
| learning_rate | FLOAT | No | Optimizer learning rate. Default: `0.0001` |
| lr_scheduler_type | STRING | No | Learning rate scheduler type. Options: `linear`, `cosine`, `cosine_with_restarts`, `polynomial`, `constant`, `constant_with_warmup` |
| logging_steps | INT | No | Log every N steps. Default: `5` |
| save_steps | INT | No | Save checkpoint every N steps. Default: `500` |
| save_total_limit | INT | No | Maximum number of checkpoints to keep. Default: `3` |
| eval_steps | INT | No | Evaluate every N steps. Default: `500` |
| seed | INT | No | Random seed. Default: `42` |
| resume_from_checkpoint | STRING | No | Checkpoint path to resume from. Default: empty string |
| max_grad_norm | FLOAT | No | Maximum gradient norm for clipping. Default: `2` |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| training_config | STRING\|TRAINING_CONFIG | Training config YAML string (`BaseTrainingConfig` fields) |
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
