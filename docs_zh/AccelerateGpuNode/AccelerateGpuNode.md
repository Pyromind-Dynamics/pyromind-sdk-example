# Accelerate GPU Node 节点

![alt text](/imgs/AccelerateGpuNode/AccelerateGpuNode.png)

## 1.1 功能概述

GPU node example using accelerate launch mode

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| message | STRING | 是 | 默认值：`Accelerate GPU Node executed successfully` |

## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| gpu_info | STRING | gpu_info |
| execution_result | STRING | execution_result |
| execution_output | STRING | execution_output |
| message_output | STRING | message_output |

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
