# Dataset Config Builder 节点

![alt text](/imgs/DatasetConfigBuilderNode/DatasetConfigBuilderNode.png)

## 1.1 功能概述

构建用于 SFT/GRPO 训练的数据集配置 YAML 字符串。该节点用于配置训练数据路径、数据加载器类型、字段映射等参数。

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| train_data_path | STRING | 是 | 训练数据路径 |
| val_data_path | STRING | 否 | 验证数据路径。默认值：空字符串 |
| dataloader_kind | STRING | 否 | 数据加载器类型。默认值：`vision` |
| image_field | STRING | 否 | 图片字段名。默认值：`image_path` |
| assistant_response_field | STRING | 否 | 助手回复字段名。默认值：`gt` |
| rejected_field | STRING | 否 | 拒绝回复字段名（DPO 用）。默认值：空字符串 |
| messages_field | STRING | 否 | 消息字段名。默认值：`messages` |
| user_prompt_field | STRING | 否 | 用户提示字段名。默认值：空字符串 |
| system_prompt_field | STRING | 否 | 系统提示字段名。默认值：空字符串 |
| sft_collator_entry | STRING | 否 | SFT 整理器入口。默认值：`train.sft_collator:make_collate_fn` |
| dpo_collator_entry | STRING | 否 | DPO 整理器入口。默认值：空字符串 |
| grpo_collator_entry | STRING | 否 | GRPO 整理器入口。默认值：空字符串 |
| max_seq_length | INT | 否 | 最大序列长度。默认值：`4096` |

## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| dataset_config | STRING | 构建的数据集配置 YAML 字符串 |

## 1.4 Workflow JSON 定义

完整 workflow 定义见 [`workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json`](../../workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json)。

示例配置：
```json
{
  "config": {
    "train_data_path": "/workspace/datasets/openai/gsm8k/",
    "val_data_path": "",
    "dataloader_kind": "vision",
    "image_field": "image_path",
    "assistant_response_field": "gt",
    "rejected_field": "",
    "messages_field": "messages",
    "user_prompt_field": "",
    "system_prompt_field": "",
    "sft_collator_entry": "train.sft_collator:make_collate_fn",
    "dpo_collator_entry": "",
    "grpo_collator_entry": "",
    "max_seq_length": 4096
  }
}
```

## 1.5 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `DatasetConfigBuilderNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |

```bash
python -m pyromind_sdk.test_run_workflow_cli workflow/DatasetConfigBuilderNode/DatasetConfigBuilderNode.json --pretty
```

输出示例：

```json
{
  "task_id": "4923",
  "task_name": "test-traindata",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 18989,
      "node_type": "DatasetConfigBuilderNode",
      "label": "",
      "start_at": "2026-06-09 09:49:32",
      "end_at": "2026-06-09 09:49:39",
      "duration": "0:00:07",
      "input": {
        "train_data_path": "/workspace/datasets/openai/gsm8k/",
        "val_data_path": "",
        "dataloader_kind": "vision",
        "image_field": "image_path",
        "assistant_response_field": "gt",
        "rejected_field": "",
        "messages_field": "messages",
        "user_prompt_field": "",
        "system_prompt_field": "",
        "sft_collator_entry": "train.sft_collator:make_collate_fn",
        "dpo_collator_entry": "",
        "grpo_collator_entry": "",
        "max_seq_length": 4096
      },
      "output": {
        "dataset_config": "train_data_path: /workspace/datasets/openai/gsm8k/\ndataloader_kind: vision\nimage_field: image_path\nassistant_response_field: gt\nrejected_field: ''\nmessages_field: messages\nsft_collator_entry: train.sft_collator:make_collate_fn\ndpo_collator_entry: ''\ngrpo_collator_entry: ''\nmax_seq_length: 4096"
      },
      "raw": {}
    }
  ]
}
```
