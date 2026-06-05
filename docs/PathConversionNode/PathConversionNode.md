# Path Conversion Node

![alt text](/imgs/PathConversionNode/PathConversionNode.png)  

## 1.1 Overview

路径转换节点：将路径从 /workspace 转换为 /target-workspace，从 /root 转换为 /target-root
    这是一个内部节点，用于处理 CUSTOMER_INPUTS 中的动态输入路径转换

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| input_path | STRING | Yes | String value. Default: - |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| output_path | STRING | String value |

## 1.4 Workflow JSON Definition

See [`workflow/PathConversionNode/PathConversionNode.json`](../../workflow/PathConversionNode/PathConversionNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/PathConversionNode/PathConversionNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `pathConversionNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
