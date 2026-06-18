# Wandb Config Builder 节点

![alt text](/imgs/WandbConfigBuilderNode/WandbConfigBuilderNode.png)

## 1.1 功能概述

构建 W&B 训练运行时环境配置 YAML 字符串（`wandb_api_key`、`wandb_project`、`wandb_name`）。

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| wandb_api_key | STRING | 是 | W&B API 密钥。默认值：`''` |
| wandb_project | STRING | 是 | W&B 项目名称。默认值：`''` |
| wandb_name | STRING | 否 | W&B run 名称。默认值：`''` |

## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| wandb_config | WANDB_CONFIG | W&B 配置 YAML |

## 1.4 Workflow JSON 定义

完整 workflow 定义见 [`workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json`](../../workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json)。

示例配置：
```json
{
  "config": {
    "wandb_api_key": "",
    "wandb_project": "test-01",
    "wandb_name": "run-001"
  }
}
```

## 1.5 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `WandbConfigBuilderNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |

```bash
python -m pyromind_sdk.test_run_workflow_cli workflow/WandbConfigBuilderNode/WandbConfigBuilderNode.json --pretty
```

输出示例：

```json
{
  "task_id": "4922",
  "task_name": "wandb",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 18988,
      "node_type": "WandbConfigBuilderNode",
      "label": "",
      "start_at": "2026-06-09 09:33:15",
      "end_at": "2026-06-09 09:33:32",
      "duration": "0:00:17",
      "input": {
        "wandb_api_key": "",
        "wandb_project": "test-01",
        "wandb_name": "run-001"
      },
      "output": {
        "wandb_config": "WANDB_PROJECT: test-01\nWANDB_NAME: run-001"
      },
      "raw": {}
    }
  ]
}
```
