# Benchmark By Api Node

![alt text](/imgs/ModelEvalApiNode/ModelEvalApiNode.png)

## 1.1 Overview

Offline model evaluation via Inference API.
Loads a benchmark dataset, batch-calls the deployed model endpoint, computes
task-level metrics (accuracy, JSON format compliance, etc.), and outputs a report
for comparing model versions before and after SFT / GRPO / DPO training.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| endpoint | STRING | Yes | Default: `http://127.0.0.1:3000/v1` |
| endpoint_api_key | STRING | Yes | Default: `empty` |
| endpoint_model | STRING | Yes | Default: `default` |
| output_path | STRING | Yes | Output directory path |
| dataset_config | STRING | Yes | Dataset configuration YAML string |
| metrics_config | STRING | Yes | - |
| max_samples | INT | No | Default: `0` |
| max_tokens | INT | No | Default: `256` |
| temperature | FLOAT | No | Sampling temperature. Default: `0.01` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| benchmark_output_path | STRING | Benchmark report output path |

## 1.4 Workflow JSON Definition

See [`workflow/ModelEvalApiNode/ModelEvalApiNode.json`](../../workflow/ModelEvalApiNode/ModelEvalApiNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ModelEvalApiNode/ModelEvalApiNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `modelEvalApiNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
