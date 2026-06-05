# Reward Config Builder 节点

![alt text](/imgs/RewardConfigBuilderNode/RewardConfigBuilderNode.png)  

## {{section}} 功能概述

Build reward config YAML from up to five reward item YAML strings and normalize flag.

## {{section}} 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| reward_item_1 | STRING | 否 | 字符串。默认值：- |
| reward_item_2 | STRING | 否 | 字符串。默认值：- |
| reward_item_3 | STRING | 否 | 字符串。默认值：- |
| reward_item_4 | STRING | 否 | 字符串。默认值：- |
| reward_item_5 | STRING | 否 | 字符串。默认值：- |
| normalize | BOOLEAN | 否 | 布尔值。默认值：`False` |
## {{section}} 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| reward_config | STRING | 字符串 |

## {{section}} Workflow JSON 定义

完整 workflow 定义见 [`workflow/RewardConfigBuilderNode/RewardConfigBuilderNode.json`](../../workflow/RewardConfigBuilderNode/RewardConfigBuilderNode.json)。

## {{section}} 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/RewardConfigBuilderNode/RewardConfigBuilderNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `rewardConfigBuilderNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
