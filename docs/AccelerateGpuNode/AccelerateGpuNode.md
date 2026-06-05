# Accelerate GPU Node Node

![alt text](/imgs/AccelerateGpuNode/AccelerateGpuNode.png)  

## {{section}} Overview

GPU node example using accelerate launch mode

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| message | STRING | Yes | String value. Default: `Accelerate GPU Node executed successfully` |
| accelerate_config | ACCELERATE_CONFIG | Yes | Accelerate configuration YAML. Default: - |
| gpu_count | INT | Yes | Integer value. Default: `1` |
| gpu_product | STRING | Yes | String value. Default: `NVIDIA-H100-NVL` Options: NVIDIA-H100-NVL, NVIDIA-L40S, NVIDIA-H200, NVIDIA-B200, NVIDIA-H100-80GB-HBM3 |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| gpu_info | STRING | String value |
| execution_result | STRING | String value |
| execution_output | STRING | String value |
| message_output | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/AccelerateGpuNode/AccelerateGpuNode.json`](../../workflow/AccelerateGpuNode/AccelerateGpuNode.json) for the full workflow definition.

## {{section}} Running the Workflow

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
