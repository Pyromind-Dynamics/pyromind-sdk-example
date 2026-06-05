# GRPO Training 节点

![alt text](/imgs/ModelTrainGRPONode/ModelTrainGRPONode.png)  

## 1.1 功能概述

GRPO training aligned with SFT-style YAML: dataset_config, training_config (shared with SFT),
grpo_extra_config (GRPO-only), model_config, reward_config. Returns output directory.

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| output_path | STRING | 是 | 字符串。默认值：- |
| dataset_config | STRING | 是 | 字符串。默认值：- |
| training_config | STRING | 是 | 字符串。默认值：- |
| model_config | STRING | 是 | 字符串。默认值：- |
| reward_config | STRING | 是 | 字符串。默认值：- |
| accelerate_config | ACCELERATE_CONFIG | 是 | Accelerate 配置 YAML。默认值：- |
| gpu_count | INT | 是 | 整数。默认值：`1` |
| gpu_product | STRING | 是 | 字符串。默认值：`NVIDIA-H100-NVL` Options: NVIDIA-H100-NVL, NVIDIA-L40S, NVIDIA-H200, NVIDIA-B200, NVIDIA-H100-80GB-HBM3 |
| grpo_extra_config | STRING | 否 | 字符串。默认值：- |
| wandb_config | WANDB_CONFIG | 否 | W&B 配置 YAML。默认值：- |
| thinking_as_input_ratio | FLOAT | 否 | 浮点数。默认值：`0.0` |
## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| model_output_path | STRING | 字符串 |

## 1.4 Workflow JSON 定义

完整 workflow 定义见 [`workflow/ModelTrainGRPONode/ModelTrainGRPONode.json`](../../workflow/ModelTrainGRPONode/ModelTrainGRPONode.json)。

## 1.5 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelTrainGRPONode/ModelTrainGRPONode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `modelTrainGRPONode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
