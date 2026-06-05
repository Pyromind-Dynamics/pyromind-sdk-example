# Validate GRPO Dataloader 节点

![alt text](/imgs/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.png)  

## 1.1 功能概述

Validate GRPO dataloader configuration, reward config, and rollout behavior.

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| dataset_config | STRING | 是 | 字符串。默认值：- |
| rollout_size | INT | 否 | 整数。默认值：`3` |
| check_reasoning | BOOLEAN | 否 | 布尔值。默认值：`False` |
| limit | INT | 否 | 整数。默认值：`0` |
| verbose | BOOLEAN | 否 | 布尔值。默认值：`False` |
| preview_html_path | STRING | 否 | 字符串。默认值：- |
| reward_config | STRING | 否 | 字符串。默认值：- |
## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| metrics_json | STRING | 字符串 |
| output_preview_path | STRING | 字符串 |

## 1.4 Workflow JSON 定义

完整 workflow 定义见 [`workflow/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.json`](../../workflow/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.json)。

## 1.5 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelValidateGRPODataloaderNode/ModelValidateGRPODataloaderNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `modelValidateGRPODataloaderNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
