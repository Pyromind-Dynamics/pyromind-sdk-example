# Content Preview Node

![alt text](/imgs/ContentPreview/ContentPreview.png)

## 1.1 Overview

Display input content in the selected file format. Use this node to preview text-like content as `txt`, `json`, `xml`, or `python`.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| content | * | Yes | Content to display |
| file_format | STRING | Yes | Preview file format. Default: `txt` Options: txt, json, xml, python |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| content | * | Original previewed content |

## 1.4 Workflow JSON Definition

See [`workflow/ContentPreview/ContentPreview.json`](../../workflow/ContentPreview/ContentPreview.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ContentPreview/ContentPreview.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `contentPreview` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
