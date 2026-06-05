# Path Conversion 节点

![alt text](/imgs/PathConversionNode/PathConversionNode.png)  

## {{section}} 功能概述

路径转换节点：将路径从 /workspace 转换为 /target-workspace，从 /root 转换为 /target-root
    这是一个内部节点，用于处理 CUSTOMER_INPUTS 中的动态输入路径转换

## {{section}} 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| input_path | STRING | 是 | 字符串。默认值：- |
## {{section}} 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| output_path | STRING | 字符串 |

## {{section}} Workflow JSON 定义

完整 workflow 定义见 [`workflow/PathConversionNode/PathConversionNode.json`](../../workflow/PathConversionNode/PathConversionNode.json)。

## {{section}} 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/PathConversionNode/PathConversionNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `pathConversionNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
