# Accelerate GPU Node Node

![alt text](/imgs/AccelerateGpuNode/AccelerateGpuNode.png)  

## 1.1 Overview

The AccelerateGpuNode is a core node used to execute Accelerate framework configuration tasks within a specified GPU hardware environment. This node receives custom messages, Accelerate YAML configuration files, and GPU resource requirement parameters. It completes initialization and execution in the underlying environment, ultimately returning detailed hardware information, execution status, and runtime logs to provide environment validation and execution feedback for subsequent distributed training or inference tasks.


## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| message | STRING | Yes | Custom execution prompt message. Default: `Accelerate GPU Node executed successfully` |
| accelerate_config | ACCELERATE_CONFIG | Yes | Accelerate configuration YAML. Default: - |
| gpu_count | INT | Yes | The number of GPUs requested for allocation, integer type.. Default: `1` |
| gpu_product | STRING | Yes | The specified GPU hardware model. Default: `NVIDIA-H100-NVL` Options: NVIDIA-H100-NVL, NVIDIA-L40S, NVIDIA-H200, NVIDIA-B200, NVIDIA-H100-80GB-HBM3 |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| gpu_info | STRING | Information about the actual GPU hardware model allocated. Default：`NVIDIA H100 NVL`|
| execution_result | STRING | The final execution result status identifier of the task. Default: `Code executed successfully`|
| execution_output | STRING | Detailed execution log output (e.g., CUDA status, GPU count, and model). Default: `Accelerate GPU Node executed successfullyCUDA available: True\nGPU count: 1\nGPU name: NVIDIA H100 NVL` |
| message_output | STRING | Comprehensive message output(e.g., CUDA status, GPU count, and model). Default: `Accelerate GPU Node executed successfullyCUDA available: True\nGPU count: 1\nGPU name: NVIDIA H100 NVL`|

## 1.4 Workflow JSON Definition

See [`workflow/AccelerateGpuNode/AccelerateGpuNode.json`](../../workflow/AccelerateGpuNode/AccelerateGpuNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/AccelerateGpuNode/AccelerateGpuNode.json --pretty
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

example  output:

```jason
{
  "task_id": "4898",
  "task_name": "unsaved-workflow",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 18931,
      "node_type": "AccelerateGpuNode",
      "label": "",
      "start_at": "2026-06-09 06:04:05",
      "end_at": "2026-06-09 06:04:59",
      "duration": "0:00:54",
      "input": {
        "message": "Accelerate GPU Node executed successfully",
        "accelerate_config": "",
        "gpu_count": 1,
        "gpu_product": "NVIDIA-H100-NVL"
      },
      "output": {
        "gpu_info": "NVIDIA H100 NVL",
        "execution_result": "Code executed successfully",
        "execution_output": "Accelerate GPU Node executed successfullyCUDA available: True\nGPU count: 1\nGPU name: NVIDIA H100 NVL",
        "message_output": "Accelerate GPU Node executed successfullyCUDA available: True\nGPU count: 1\nGPU name: NVIDIA H100 NVL"
      },
      "raw": {}
    },
    {
      "node_key": "#2",
      "node_id": 18930,
      "node_type": "AccelerateConfigBuilderNode",
      "label": "",
      "start_at": "2026-06-09 06:03:45",
      "end_at": "2026-06-09 06:03:56",
      "duration": "0:00:11",
      "input": {
        "zero_stage": 1,
        "gpu_count": 1
      },
      "output": {
        "accelerate_config": "compute_environment: LOCAL_MACHINE\ndebug: false\ndeepspeed_config:\n  zero3_init_flag: false\n  zero_stage: 1\ndistributed_type: DEEPSPEED\nenable_cpu_affinity: true\nmachine_rank: 0\nmain_training_function: main\nnum_machines: 1\nnum_processes: 1\nrdzv_backend: static\nsame_network: true\nmixed_precision: bf16"
      },
      "raw": {}
    }
  ]
}
```