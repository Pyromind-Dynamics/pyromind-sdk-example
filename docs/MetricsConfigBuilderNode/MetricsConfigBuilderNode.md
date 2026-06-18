# Metrics Config Builder(System Entry) Node

![alt text](/imgs/MetricsConfigBuilderNode/MetricsConfigBuilderNode.png)

## 1.1 Overview

Build a metrics config as YAML.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| entry | STRING | Yes | Default: `compute_gsm8k`. Options: compute_gsm8k, compute_accuracy, compute_bleu, compute_rouge_l |
| name | STRING | Yes | Default: `''` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| metrics_config | STRING | Built metrics configuration YAML string |

## 1.4 Workflow JSON Definition

See [`workflow/MetricsConfigBuilderNode/MetricsConfigBuilderNode.json`](../../workflow/MetricsConfigBuilderNode/MetricsConfigBuilderNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/MetricsConfigBuilderNode/MetricsConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `metricsConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
