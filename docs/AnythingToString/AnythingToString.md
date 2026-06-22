# Anything to String Node

![alt text](/imgs/AnythingToString/AnythingToString.png)  

## 1.1 Overview

Convert any input type to string. Simply passes through the input value as string.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| anything | * | Yes | Any type. Default: "" (empty string) |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| string | STRING | String representation of the input value. |

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

```bash
python -m pyromind_sdk.test_run_workflow_cli workflow/AnythingToString/AnythingToString.json --pretty
```

Example output:

```json
{
  "task_id": "4924",
  "task_name": "unsaved-workflow",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 18991,
      "node_type": "AnythingToString",
      "label": "",
      "start_at": "2026-06-09 09:56:20",
      "end_at": "2026-06-09 09:56:31",
      "duration": "0:00:11",
      "input": {
        "anything": ""
      },
      "output": {
        "string": "111"
      },
      "raw": {}
    },
    {
      "node_key": "#2",
      "node_id": 18990,
      "node_type": "StringToAnything",
      "label": "",
      "start_at": "2026-06-09 09:56:10",
      "end_at": "2026-06-09 09:56:15",
      "duration": "0:00:05",
      "input": {
        "input_string": "111"
      },
      "output": {
        "anything": "111"
      },
      "raw": {}
    }
  ]
}
```
