# Wandb Config Builder Node

![alt text](/imgs/WandbConfigBuilderNode/WandbConfigBuilderNode.png)  

## {{section}} Overview

Build wandb_config YAML string for W&B training runtime env.

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| wandb_api_key | STRING | No | String value. Default: - |
| wandb_project | STRING | No | String value. Default: - |
| wandb_run_group | STRING | No | String value. Default: - |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| wandb_config | WANDB_CONFIG | W&B configuration YAML |

## {{section}} Workflow JSON Definition

See [`workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json`](../../workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `wandbConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
