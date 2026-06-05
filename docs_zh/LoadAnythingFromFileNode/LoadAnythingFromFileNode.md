# Load Anything From File 节点

![alt text](/imgs/LoadAnythingFromFileNode/LoadAnythingFromFileNode.png)  

## {{section}} 功能概述

Load content from a file path.

## {{section}} 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| file_path | STRING | 是 | 字符串。默认值：- |
| encoding | STRING | 否 | 字符串。默认值：`utf-8` |
## {{section}} 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| loaded_file_path | STRING | 字符串 |
| content | * | 任意类型 |
| read_bytes | INT | 整数 |

## {{section}} Workflow JSON 定义

完整 workflow 定义见 [`workflow/LoadAnythingFromFileNode/LoadAnythingFromFileNode.json`](../../workflow/LoadAnythingFromFileNode/LoadAnythingFromFileNode.json)。

## {{section}} 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/LoadAnythingFromFileNode/LoadAnythingFromFileNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `loadAnythingFromFileNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
