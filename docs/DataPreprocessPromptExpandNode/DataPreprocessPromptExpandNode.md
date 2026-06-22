# Prompt Augmentation Node

![alt text](/imgs/DataPreprocessPromptExpandNode/DataPreprocessPromptExpandNode.png)

## 1.1 Overview

Run data_preprocess prompt-expand pipeline and emit output path.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| input_path | STRING | Yes | Input path |
| output_path | STRING | Yes | Output directory or file path |
| user_prompt | STRING | No | User prompt |
| user_prompt_column | STRING | No | User prompt column. Default: empty string |
| format_lang | STRING | No | Format lang. Default: `en` |
| api_base | STRING | Yes | Api base |
| model | STRING | Yes | Model |
| api_key | STRING | Yes | Api key |
| system_prompt | STRING | No | System prompt. Default: empty string |
| max_tokens | INT | No | Maximum tokens per API completion. Default: `1024` |
| thinking | BOOLEAN | No | Thinking. Default: false |
| limit | INT | No | Max samples for validation preview (0 = no limit). Default: `0` |
| concurrency | INT | No | Concurrency. Default: `1` |
| num_variations | INT | No | Num variations. Default: `1` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| augmentation_path | STRING | Prompt expansion output path |

## 1.4 Workflow JSON Definition

See [`workflow/DataPreprocessPromptExpandNode/DataPreprocessPromptExpandNode.json`](../../workflow/DataPreprocessPromptExpandNode/DataPreprocessPromptExpandNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DataPreprocessPromptExpandNode/DataPreprocessPromptExpandNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `dataPreprocessPromptExpandNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
