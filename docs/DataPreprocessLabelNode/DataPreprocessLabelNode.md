# DataPreprocessLabelNode Node

![alt text](/imgs/DataPreprocessLabelNode/DataPreprocessLabelNode.png)  

## 1.1 Overview

Run data_preprocess label pipeline and emit output path.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| input_path | STRING | Yes | String value. Default: - |
| output_path | STRING | Yes | String value. Default: - |
| api_base | STRING | Yes | String value. Default: - |
| model | STRING | Yes | String value. Default: - |
| api_key | STRING | Yes | String value. Default: - |
| system_prompt | STRING | No | String value. Default: - |
| format_lang | STRING | No | String value. Default: `en` |
| extract | STRING | No | String value. Default: `boxed` |
| max_tokens | INT | No | Integer value. Default: `1024` |
| thinking | BOOLEAN | No | Boolean flag (true/false). Default: `False` |
| limit | INT | No | Integer value. Default: `0` |
| concurrency | INT | No | Integer value. Default: `1` |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| result_output_path | STRING | String value |

## 1.4 Workflow JSON Definition

See [`workflow/DataPreprocessLabelNode/DataPreprocessLabelNode.json`](../../workflow/DataPreprocessLabelNode/DataPreprocessLabelNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DataPreprocessLabelNode/DataPreprocessLabelNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `dataPreprocessLabelNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
