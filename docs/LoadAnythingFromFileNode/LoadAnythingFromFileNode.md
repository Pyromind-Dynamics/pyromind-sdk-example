# Load Anything From File Node

![alt text](/imgs/LoadAnythingFromFileNode/LoadAnythingFromFileNode.png)  

## {{section}} Overview

Load content from a file path.

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| file_path | STRING | Yes | String value. Default: - |
| encoding | STRING | No | String value. Default: `utf-8` |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| loaded_file_path | STRING | String value |
| content | * | Any type |
| read_bytes | INT | Integer value |

## {{section}} Workflow JSON Definition

See [`workflow/LoadAnythingFromFileNode/LoadAnythingFromFileNode.json`](../../workflow/LoadAnythingFromFileNode/LoadAnythingFromFileNode.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/LoadAnythingFromFileNode/LoadAnythingFromFileNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `loadAnythingFromFileNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
