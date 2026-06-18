# Model Config Builder Node

![alt text](/imgs/ModelConfigBuilderNode/ModelConfigBuilderNode.png)

## 1.1 Overview

Builds model config YAML string (`model_path`, `model_type`).

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| model_path | STRING | Yes | Base model path or HuggingFace model ID. Default: `''` |
| model_type | STRING | No | Default: `auto`. Options: auto, qwen3vl, qwen3.5 |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| model_config | STRING | Built model configuration YAML string |

## 1.4 Workflow JSON Definition

See [`workflow/ModelConfigBuilderNode/ModelConfigBuilderNode.json`](../../workflow/ModelConfigBuilderNode/ModelConfigBuilderNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelConfigBuilderNode/ModelConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `modelConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
