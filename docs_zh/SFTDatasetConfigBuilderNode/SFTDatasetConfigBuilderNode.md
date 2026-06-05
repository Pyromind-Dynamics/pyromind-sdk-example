# SFT Dataset Config Builder 节点

![alt text](/imgs/SFTDatasetConfigBuilderNode/SFTDatasetConfigBuilderNode.png)  

## 1.1 功能概述

Build SFT dataset config YAML string.

## 1.2 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| train_data_path | STRING | 是 | 字符串。默认值：- |
| val_data_path | STRING | 否 | 字符串。默认值：- |
| dataloader_kind | STRING | 否 | 字符串。默认值：`vision` |
| image_field | STRING | 否 | 字符串。默认值：`image_path` |
| text_field | STRING | 否 | 字符串。默认值：`text` |
| messages_field | STRING | 否 | 字符串。默认值：`messages` |
| user_prompt_field | STRING | 否 | 字符串。默认值：- |
| system_prompt_field | STRING | 否 | 字符串。默认值：- |
| collator_entry | STRING | 否 | 字符串。默认值：`train.sft_collator:make_collate_fn` |
| max_seq_length | INT | 否 | 整数。默认值：`4096` |
## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| dataset_config | STRING | 字符串 |

## 1.4 Workflow JSON 定义

完整 workflow 定义见 [`workflow/SFTDatasetConfigBuilderNode/SFTDatasetConfigBuilderNode.json`](../../workflow/SFTDatasetConfigBuilderNode/SFTDatasetConfigBuilderNode.json)。

## 1.5 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/SFTDatasetConfigBuilderNode/SFTDatasetConfigBuilderNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `sFTDatasetConfigBuilderNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
