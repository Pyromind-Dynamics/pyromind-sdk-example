# Anything to String Node

![alt text](/imgs/AnythingToString/AnythingToString.png)  

## 1.1 Overview

任意类型转字符串节点：将任何类型的输入转换为字符串输出
    这是一个通用的转换节点，用于将 MODEL、STRING 等类型转换为 STRING

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| anything | * | Yes | Any type. Default: - |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| string | STRING | String value |

## 1.4 Workflow JSON Definition

See [`workflow/AnythingToString/AnythingToString.json`](../../workflow/AnythingToString/AnythingToString.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/AnythingToString/AnythingToString.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `anythingToString` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
