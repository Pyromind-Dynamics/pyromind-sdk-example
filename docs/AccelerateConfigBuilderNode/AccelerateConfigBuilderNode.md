# Accelerate Config Builder Node

![alt text](/imgs/AccelerateConfigBuilderNode/AccelerateConfigBuilderNode.png)  

## {{section}} Overview

Build accelerate_config YAML string for accelerate launch.

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| zero_stage | INT | No | Integer value. Default: `2` |
| gpu_count | INT | No | Integer value. Default: `4` |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| accelerate_config | ACCELERATE_CONFIG | Accelerate configuration YAML |

## {{section}} Workflow JSON Definition

See [`workflow/AccelerateConfigBuilderNode/AccelerateConfigBuilderNode.json`](../../workflow/AccelerateConfigBuilderNode/AccelerateConfigBuilderNode.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/AccelerateConfigBuilderNode/AccelerateConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `accelerateConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
