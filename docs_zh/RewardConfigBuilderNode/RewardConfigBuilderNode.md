# Reward Config Builder 节点

![alt text](/imgs/RewardConfigBuilderNode/RewardConfigBuilderNode.png)  

## 1.1 功能概述

Build reward config YAML from up to five reward item YAML strings and normalize flag.

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| reward_item_1 | STRING | 否 | 字符串。默认值：- |
| reward_item_2 | STRING | 否 | 字符串。默认值：- |
| reward_item_3 | STRING | 否 | 字符串。默认值：- |
| reward_item_4 | STRING | 否 | 字符串。默认值：- |
| reward_item_5 | STRING | 否 | 字符串。默认值：- |
| normalize | BOOLEAN | 否 | 布尔值。默认值：`False` |
## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| reward_config | STRING | 字符串 |

## 1.4 Workflow JSON 定义

完整 workflow 定义见 [`workflow/RewardConfigBuilderNode/RewardConfigBuilderNode.json`](../../workflow/RewardConfigBuilderNode/RewardConfigBuilderNode.json)。

## 1.5 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/RewardConfigBuilderNode/RewardConfigBuilderNode.json --pretty
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



输出示例：

```json

{
  "task_id": "4870",
  "task_name": "unsaved-workflow",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 18872,
      "node_type": "RewardConfigBuilderNode",
      "label": "",
      "start_at": "2026-06-09 02:53:42",
      "end_at": "2026-06-09 02:54:10",
      "duration": "0:00:28",
      "input": {
        "reward_item_1": "{\"name\": \"goal_distance_reward\", \"type\": \"euclidean_distance\", \"target_key\": \"goal_position\", \"weight\": 5.0, \"clip_min\": 0.0, \"clip_max\": 10.0}",
        "reward_item_2": "{\"name\": \"goal_distance_reward\", \"type\": \"euclidean_distance\", \"target_key\": \"goal_position\", \"weight\": 5.0, \"clip_min\": 0.0, \"clip_max\": 10.0}",
        "reward_item_3": "{\"name\": \"goal_distance_reward\", \"type\": \"euclidean_distance\", \"target_key\": \"goal_position\", \"weight\": 5.0, \"clip_min\": 0.0, \"clip_max\": 10.0}",
        "reward_item_4": "{\"name\": \"goal_distance_reward\", \"type\": \"euclidean_distance\", \"target_key\": \"goal_position\", \"weight\": 5.0, \"clip_min\": 0.0, \"clip_max\": 10.0}",
        "reward_item_5": "{\"name\": \"goal_distance_reward\", \"type\": \"euclidean_distance\", \"target_key\": \"goal_position\", \"weight\": 5.0, \"clip_min\": 0.0, \"clip_max\": 10.0}",
        "normalize": false
      },
      "output": {
        "reward_config": "normalize: false\nitems:\n- name: goal_distance_reward\n  type: euclidean_distance\n  target_key: goal_position\n  weight: 5.0\n  clip_min: 0.0\n  clip_max: 10.0\n- name: goal_distance_reward\n  type: euclidean_distance\n  target_key: goal_position\n  weight: 5.0\n  clip_min: 0.0\n  clip_max: 10.0\n- name: goal_distance_reward\n  type: euclidean_distance\n  target_key: goal_position\n  weight: 5.0\n  clip_min: 0.0\n  clip_max: 10.0\n- name: goal_distance_reward\n  type: euclidean_distance\n  target_key: goal_position\n  weight: 5.0\n  clip_min: 0.0\n  clip_max: 10.0\n- name: goal_distance_reward\n  type: euclidean_distance\n  target_key: goal_position\n  weight: 5.0\n  clip_min: 0.0\n  clip_max: 10.0"
      },
      "raw": {}
    }
  ]
}


```