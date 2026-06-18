# Accelerate Config Builder Node

![alt text](/imgs/AccelerateConfigBuilderNode/AccelerateConfigBuilderNode.png)

## 1.1 Overview

Build accelerate_config YAML string for accelerate launch.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| zero_stage | INT | No | Default: `2` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| accelerate_config | ACCELERATE_CONFIG | Accelerate configuration YAML |

## 1.4 Workflow JSON Definition

See [`workflow/AccelerateConfigBuilderNode/AccelerateConfigBuilderNode.json`](../../workflow/AccelerateConfigBuilderNode/AccelerateConfigBuilderNode.json) for the full workflow definition.

## 1.5 Running the Workflow

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
