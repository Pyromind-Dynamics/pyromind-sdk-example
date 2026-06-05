# SFT Model Config Builder 节点

![alt text](/imgs/SFTModelConfigBuilderNode/SFTModelConfigBuilderNode.png)  

## {{section}} 功能概述

Build SFT model config YAML string.

## {{section}} 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| model_name | STRING | 否 | 字符串。默认值：`Qwen/Qwen3-VL-2B-Instruct` |
| model_type | STRING | 否 | 字符串。默认值：`auto` |
| lora_rank | INT | 否 | 整数。默认值：`8` |
| full_finetune | BOOLEAN | 否 | 布尔值。默认值：`False` |
## {{section}} 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| model_config | STRING | 字符串 |

## {{section}} Workflow JSON 定义

完整 workflow 定义见 [`workflow/SFTModelConfigBuilderNode/SFTModelConfigBuilderNode.json`](../../workflow/SFTModelConfigBuilderNode/SFTModelConfigBuilderNode.json)。

## {{section}} 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/SFTModelConfigBuilderNode/SFTModelConfigBuilderNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `sFTModelConfigBuilderNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
