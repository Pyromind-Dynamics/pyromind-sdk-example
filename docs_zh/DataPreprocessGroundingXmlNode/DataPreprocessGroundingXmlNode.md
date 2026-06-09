# Grounding XML Generation 节点

![alt text](/imgs/DataPreprocessGroundingXmlNode/DataPreprocessGroundingXmlNode.png)  

## 1.1 功能概述

Run data_preprocess grounding-xml pipeline and emit output path.

## 1.2 输入类型

| 参数 | 数据类型    | 必填 | 描述                                                                                                                         |
|------|---------|----|----------------------------------------------------------------------------------------------------------------------------|
| accelerate_config | STRING  | 是  | 字符串。默认值：-                                                                                                                  |
| wandb_config | STRING    | 否  | YAML mapping格式，wandb参数示例：<br/> WANDB_API_KEY: ********<br/>WANDB_PROJECT: [Your Project]<br/>WANDB_RUN_GROUP: [Your Group] |
| image_dir | STRING  | 是  | 字符串。默认值：-                                                                                                                  |
| output_dir | STRING  | 是  | 字符串。默认值：-                                                                                                                  |
| api_base | STRING  | 是  | 字符串。默认值：-                                                                                                                  |
| model | STRING  | 是  | 字符串。默认值：-                                                                                                                  |
| api_key | STRING  | 是  | 字符串。默认值：-                                                                                                                  |
| system_prompt | STRING  | 否  | 字符串。默认值：-                                                                                                                  |
| max_tokens | INT     | 否  | 整数。默认值：`2048`                                                                                                              |
| thinking | BOOLEAN | 否  | 布尔值。默认值：`False`                                                                                                            |
| concurrency | INT     | 否  | 整数。默认值：`8`                                                                                                                 |
## 1.3 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| result_output_path | STRING | 字符串 |

## 1.4 Workflow JSON 定义

完整 workflow 定义见 [`workflow/DataPreprocessGroundingXmlNode/DataPreprocessGroundingXmlNode.json`](../../workflow/DataPreprocessGroundingXmlNode/DataPreprocessGroundingXmlNode.json)。

## 1.5 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DataPreprocessGroundingXmlNode/DataPreprocessGroundingXmlNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `dataPreprocessGroundingXmlNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
