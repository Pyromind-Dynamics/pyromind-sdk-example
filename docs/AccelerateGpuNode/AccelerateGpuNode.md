# Accelerate GPU Node

![alt text](/imgs/AccelerateGpuNode/AccelerateGpuNode.png)

## 1.1 Overview

GPU node example using accelerate launch mode

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| message | STRING | Yes | Message |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| gpu_info | STRING | GPU information string |
| execution_result | STRING | Command execution result |
| execution_output | STRING | Command stdout/stderr output |
| message_output | STRING | Status message |

## 1.4 Workflow JSON Definition

See [`workflow/AccelerateGpuNode/AccelerateGpuNode.json`](../../workflow/AccelerateGpuNode/AccelerateGpuNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/AccelerateGpuNode/AccelerateGpuNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `accelerateGpuNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
