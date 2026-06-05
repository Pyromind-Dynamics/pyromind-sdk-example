# Train-Validation Split Node

![alt text](/imgs/DataPreprocessSplitNode/DataPreprocessSplitNode.png)  

## 1.1 Overview

Split metadata into train and validation datasets from a shared output path template

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| input_path | STRING | Yes | String value. Default: - |
| output_path | STRING | Yes | String value. Default: - |
| train_ratio | FLOAT | No | Floating point number. Default: `0.8` |
| seed | INT | No | Integer value. Default: `42` |
| shuffle | BOOLEAN | No | Boolean flag (true/false). Default: `True` |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| train_output_path | STRING | String value |
| val_output_path | STRING | String value |

## 1.4 Workflow JSON Definition

See [`workflow/DataPreprocessSplitNode/DataPreprocessSplitNode.json`](../../workflow/DataPreprocessSplitNode/DataPreprocessSplitNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DataPreprocessSplitNode/DataPreprocessSplitNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `dataPreprocessSplitNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
