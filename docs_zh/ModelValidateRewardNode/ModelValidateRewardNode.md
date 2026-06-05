# Validate Reward 节点

![alt text](/imgs/ModelValidateRewardNode/ModelValidateRewardNode.png)  

## {{section}} 功能概述

Validate reward composition and score aggregation.

## {{section}} 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| reward_items | STRING | 是 | 字符串。默认值：- |
| normalize | BOOLEAN | 否 | 布尔值。默认值：`False` |
| completions | STRING | 否 | 字符串。默认值：- |
## {{section}} 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| status | STRING | 字符串 |
| scores | STRING | 字符串 |

## {{section}} Workflow JSON 定义

完整 workflow 定义见 [`workflow/ModelValidateRewardNode/ModelValidateRewardNode.json`](../../workflow/ModelValidateRewardNode/ModelValidateRewardNode.json)。

## {{section}} 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelValidateRewardNode/ModelValidateRewardNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `modelValidateRewardNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
