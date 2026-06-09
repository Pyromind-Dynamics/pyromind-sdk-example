# Accelerate GPU Node 节点

![alt text](/imgs/AccelerateGpuNode/AccelerateGpuNode.png)  

## 1.1 功能概述

AccelerateGpuNode 是用于在指定 GPU 硬件环境下执行 Accelerate 框架配置任务的核心节点。该节点接收自定义消息、Accelerate 的 YAML 配置文件以及 GPU 资源需求参数，在底层环境中完成初始化与运行，并最终返回详细的硬件信息、执行状态及运行日志，为后续的分布式训练或推理任务提供环境验证与执行反馈。

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| message | STRING | 是 | 自定义的执行提示消息。默认值：`Accelerate GPU Node executed successfully` |
| accelerate_config | ACCELERATE_CONFIG | 是 | Accelerate 配置 YAML文件参数内容。默认值：- |
| gpu_count | INT | 是 | 请求分配的 GPU 数量，整数类型。默认值：`1` |
| gpu_product | STRING | 是 | 指定所需的 GPU 硬件型号。默认值：`NVIDIA-H100-NVL` Options: NVIDIA-H100-NVL, NVIDIA-L40S, NVIDIA-H200, NVIDIA-B200, NVIDIA-H100-80GB-HBM3 |
## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| gpu_info | STRING | 实际分配到的 GPU 硬件型号信息。默认值：`NVIDIA H100 NVL` |
| execution_result | STRING | 任务的最终执行结果状态标识。默认值：`ode executed successfully`|
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
