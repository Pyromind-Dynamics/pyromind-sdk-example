# DataPreprocessLabelNode Node

![alt text](/imgs/DataPreprocessLabelNode/DataPreprocessLabelNode.png)

## 1.1 Overview

Run data_preprocess label pipeline and emit output path.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| input_path | STRING | Yes | - |
| output_path | STRING | Yes | Output directory path |
| api_base | STRING | Yes | - |
| model | STRING | Yes | - |
| api_key | STRING | Yes | - |
| system_prompt | STRING | No | Default: `''` |
| format_lang | STRING | No | Default: `en` |
| extract | STRING | No | Default: `boxed` |
| max_tokens | INT | No | Default: `1024` |
| thinking | BOOLEAN | No | Default: `false` |
| limit | INT | No | Default: `0` |
| concurrency | INT | No | Default: `1` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| result_output_path | STRING | result_output_path |

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
