# Prompt & Reasoning Merge 节点

![alt text](/imgs/DataPreprocessMergeNode/DataPreprocessMergeNode.png)  

## {{section}} 功能概述

Merge reasoning/category/prompts into training data.

## {{section}} 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| metadata_path | STRING | 是 | 字符串。默认值：- |
| output_path | STRING | 是 | 字符串。默认值：- |
| reasoning_path | STRING | 是 | 字符串。默认值：- |
| base_prompt | STRING | 否 | 字符串。默认值：- |
| output_format | STRING | 否 | 字符串。默认值：`jsonl` |
| base_prompt_file | STRING | 否 | 字符串。默认值：- |
| category_annotations | STRING | 否 | 字符串。默认值：- |
| prompt_augmentation_path | STRING | 否 | 字符串。默认值：- |
| system_prompt | STRING | 否 | 字符串。默认值：- |
| system_prompt_file | STRING | 否 | 字符串。默认值：- |
| copy_columns | STRING | 否 | 字符串。默认值：- |
| label_column | STRING | 否 | 字符串。默认值：`component_type` |
| gt_column | STRING | 否 | 字符串。默认值：`text` |
## {{section}} 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| result_output_path | STRING | 字符串 |

## {{section}} Workflow JSON 定义

完整 workflow 定义见 [`workflow/DataPreprocessMergeNode/DataPreprocessMergeNode.json`](../../workflow/DataPreprocessMergeNode/DataPreprocessMergeNode.json)。

## {{section}} 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DataPreprocessMergeNode/DataPreprocessMergeNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `dataPreprocessMergeNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
