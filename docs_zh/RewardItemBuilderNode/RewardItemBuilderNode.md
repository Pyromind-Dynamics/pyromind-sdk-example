# Reward Item Builder 节点

![alt text](/imgs/RewardItemBuilder/RewardItemBuilder.png)  

## 1.1 功能概述

以 YAML 格式构建单个奖励项（包含 entry、name、kwargs、weight 四个字段）。kwargs 非空时自动启用工厂模式（factory=true）；kwargs 为空时禁用工厂模式（factory=false）。

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| entry | STRING | 否 | 奖励函数入口路径，例如 `train.reward_fn:my_reward`。运行时不可为空，否则抛出 ValueError。默认值：`''` |
| name | STRING | 否 | 奖励项的可选名称标识。默认值：`''` |
| kwargs | STRING | 否 | 传递给奖励函数的关键字参数的 YAML mapping 字符串。非空时自动启用工厂模式。默认值：`''` |
| weight | FLOAT | 否 | 该奖励项在组合奖励分数中的权重系数。默认值：`1.0` |
## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| reward_item | STRING | YAML 格式的字符串，表示配置完成的奖励项。包含字段：`entry`、`source`（固定为 `python_path`）、`weight`、`factory`、`kwargs`，以及可选的 `name`。可传递给下游奖励配置节点。 |

## 1.4 Workflow JSON 定义

完整 workflow 定义见 [`workflow/RewardItemBuilder/RewardItemBuilder.json`](../../workflow/RewardItemBuilder/RewardItemBuilder.json)。

## 1.5 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/RewardItemBuilder/RewardItemBuilder.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `rewardItemBuilderNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |

```bash
python -m pyromind_sdk.test_run_workflow_cli workflow/RewardItemBuilder/RewardItemBuilder.json --pretty
```

输出示例：

```json
{
  "task_id": "4878",
  "task_name": "rewarditembuildertest",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 18888,
      "node_type": "RewardItemBuilderNode",
      "label": "",
      "start_at": "2026-06-09 03:25:37",
      "end_at": "2026-06-09 03:25:51",
      "duration": "0:00:14",
      "input": {
        "entry": "/workspace/py/example_valid_node.py",
        "name": "example_valid_node",
        "kwargs": "",
        "weight": 1
      },
      "output": {
        "reward_item": "entry: /workspace/py/example_valid_node.py\nsource: python_path\nweight: 1.0\nfactory: false\nkwargs: {}\nname: example_valid_node"
      },
      "raw": {}
    }
  ]
}
```
