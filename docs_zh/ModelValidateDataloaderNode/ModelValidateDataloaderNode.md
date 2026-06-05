# Validate Dataloader 节点

![alt text](/imgs/ModelValidateDataloaderNode/ModelValidateDataloaderNode.png)  

## {{section}} 功能概述

Validate dataloader configuration and sample readability.

## {{section}} 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| data_path | STRING | 是 | 字符串。默认值：- |
| dataloader_kind | STRING | 是 | 字符串。默认值：- |
| image_field | STRING | 否 | 字符串。默认值：`image_path` |
| text_field | STRING | 否 | 字符串。默认值：`text` |
| target_field | STRING | 否 | 字符串。默认值：`text` |
| messages_field | STRING | 否 | 字符串。默认值：`messages` |
| component_type_field | STRING | 否 | 字符串。默认值：- |
## {{section}} 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| status | STRING | 字符串 |
| metrics | STRING | 字符串 |

## {{section}} Workflow JSON 定义

完整 workflow 定义见 [`workflow/ModelValidateDataloaderNode/ModelValidateDataloaderNode.json`](../../workflow/ModelValidateDataloaderNode/ModelValidateDataloaderNode.json)。

## {{section}} 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelValidateDataloaderNode/ModelValidateDataloaderNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `modelValidateDataloaderNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
