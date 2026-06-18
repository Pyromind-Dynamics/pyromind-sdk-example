# Metrics Config Builder(Custom Entry) Node

![alt text](/imgs/MetricsConfigBuilderCustomNode/MetricsConfigBuilderCustomNode.png)

## 1.1 Overview

Build a metrics config as YAML.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| entry | STRING | Yes | Default: `''` |
| name | STRING | Yes | Default: `''` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| metrics_config | STRING | Built metrics configuration YAML string |

## 1.4 Workflow JSON Definition

See [`workflow/MetricsConfigBuilderCustomNode/MetricsConfigBuilderCustomNode.json`](../../workflow/MetricsConfigBuilderCustomNode/MetricsConfigBuilderCustomNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/MetricsConfigBuilderCustomNode/MetricsConfigBuilderCustomNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `metricsConfigBuilderCustomNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
