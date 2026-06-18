# Merge LoRA 节点

![alt text](/imgs/ModelMergeLoraNode/ModelMergeLoraNode.png)

## 1.1 功能概述

Merge LoRA adapter into base weights (PEFT merge_and_unload) and save model + processor
to a standalone directory. Base model id/path may be omitted if adapter_config.json
contains base_model_name_or_path.

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| lora_path | STRING | 是 | LoRA adapter 目录路径 |
| output_path | STRING | 是 | 输出目录路径 |
| model_path | STRING | 是 | 模型路径或 HuggingFace 模型 ID。默认值：`''` |
| model_type | STRING | 否 | 默认值：`auto`。可选值：auto, qwen3vl, qwen3.5 |

## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| merged_model_path | STRING | 合并后模型输出路径 |

## 1.4 Workflow JSON 定义

完整 workflow 定义见 [`workflow/ModelMergeLoraNode/ModelMergeLoraNode.json`](../../workflow/ModelMergeLoraNode/ModelMergeLoraNode.json)。

## 1.5 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelMergeLoraNode/ModelMergeLoraNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `modelMergeLoraNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
