# Accelerate GPU Node 节点

![alt text](/imgs/AccelerateGpuNode/AccelerateGpuNode.png)  

## 1.1 功能概述

AccelerateGpuNode 是用于在指定 GPU 硬件环境下执行 Accelerate 框架配置任务的核心节点。该节点接收自定义消息、Accelerate 的 YAML 配置文件以及 GPU 资源需求参数，在底层环境中完成初始化与运行，并最终返回详细的硬件信息、执行状态及运行日志，为后续的分布式训练或推理任务提供环境验证与执行反馈。

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| message | STRING | 是 | 自定义的执行提示消息。默认值：`Accelerate GPU Node executed successfully` |
| accelerate_config | ACCELERATE_CONFIG | 是 | Accelerate YAML 配置字符串。通常由 `AccelerateConfigBuilderNode` 节点生成。详见 §1.2.1。默认值：- |
| gpu_count | INT | 是 | 请求分配的 GPU 数量，整数类型。默认值：`1` |
| gpu_product | STRING | 是 | 指定所需的 GPU 硬件型号。默认值：`NVIDIA-H100-NVL` Options: NVIDIA-H100-NVL, NVIDIA-L40S, NVIDIA-H200, NVIDIA-B200, NVIDIA-H100-80GB-HBM3 |

### 1.2.1 AccelerateConfigBuilderNode 参数

`accelerate_config` 通常由 **AccelerateConfigBuilderNode** 节点生成，包含以下可配置参数：

| 参数 | 数据类型 | 默认值 | 描述 |
|------|---------|--------|------|
| zero_stage | INT | `2` | DeepSpeed ZeRO 优化阶段 |
| gpu_count | INT | `4` | 进程数量，映射到 YAML 中的 `num_processes` |

生成的 YAML 示例：

```yaml
compute_environment: LOCAL_MACHINE
debug: false
deepspeed_config:
  zero3_init_flag: false
  zero_stage: 2
distributed_type: DEEPSPEED
enable_cpu_affinity: true
machine_rank: 0
main_training_function: main
num_machines: 1
num_processes: 4
rdzv_backend: static
same_network: true
mixed_precision: bf16
```

## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| gpu_info | STRING | 实际分配到的 GPU 硬件型号信息。默认值：`NVIDIA H100 NVL` |
| execution_result | STRING | 任务的最终执行结果状态标识。默认值：`Code executed successfully`|
| execution_output | STRING | 详细的执行日志输出（如 CUDA 状态、GPU 数量及型号）。默认值：`Accelerate GPU Node executed successfullyCUDA available: True\nGPU count: 1\nGPU name: NVIDIA H100 NVL` |
| message_output | STRING | 综合消息输出（如 CUDA 状态、GPU 数量及型号）。默认值：`Accelerate GPU Node executed successfullyCUDA available: True\nGPU count: 1\nGPU name: NVIDIA H100 NVL`  |

## 1.4 Workflow JSON 定义

完整 workflow 定义见 [`workflow/AccelerateGpuNode/AccelerateGpuNode.json`](../../workflow/AccelerateGpuNode/AccelerateGpuNode.json)。

## 1.5 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/AccelerateGpuNode/AccelerateGpuNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `accelerateGpuNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |



```bash
python -m pyromind_sdk.test_run_workflow_cli workflow/AccelerateGpuNode/AccelerateGpuNode.json --pretty
```

输出示例：

```json
{
  "task_id": "5045",
  "task_name": "accelerategpunode",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 19379,
      "node_type": "AccelerateGpuNode",
      "label": "",
      "start_at": "2026-06-11 02:08:03",
      "end_at": "2026-06-11 02:08:33",
      "duration": "0:00:30",
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
      "node_id": 19378,
      "node_type": "AccelerateConfigBuilderNode",
      "label": "",
      "start_at": "2026-06-11 02:07:38",
      "end_at": "2026-06-11 02:07:55",
      "duration": "0:00:17",
      "input": {
        "zero_stage": 2,
        "gpu_count": 4
      },
      "output": {
        "accelerate_config": "compute_environment: LOCAL_MACHINE\ndebug: false\ndeepspeed_config:\n  zero3_init_flag: false\n  zero_stage: 2\ndistributed_type: DEEPSPEED\nenable_cpu_affinity: true\nmachine_rank: 0\nmain_training_function: main\nnum_machines: 1\nnum_processes: 4\nrdzv_backend: static\nsame_network: true\nmixed_precision: bf16"
      },
      "raw": {}
    }
  ]
}
