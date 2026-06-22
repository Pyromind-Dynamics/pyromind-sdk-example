# URL Check Node

![alt text](/imgs/CheckUrlNode/CheckUrlNode.png)  

## 1.1 Overview

Check URL node: verifies whether a URL is reachable.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| url | STRING | Yes | String value. Default: `http://localhost:3000` |
| max_retries | INT | Yes | Integer value. Default: `30` |
| retry_interval | INT | Yes | Integer value. Default: `2` |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| endpoint | STRING | String value |

## 1.4 Workflow JSON Definition

See [`workflow/CheckUrlNode/CheckUrlNode.json`](../../workflow/CheckUrlNode/CheckUrlNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/CheckUrlNode/CheckUrlNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `checkUrlNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
