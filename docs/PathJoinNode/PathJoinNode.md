# Join Path Node

![alt text](/imgs/PathJoinNode/PathJoinNode.png)  

## {{section}} Overview


> **TODO**: Add overview description


## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| base_path | STRING | Yes | String value. Default: - |
| subpath | STRING | Yes | String value. Default: - |
| environment | ENV | No | Environment variable name. Default: - |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| joined_path | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/PathJoinNode/PathJoinNode.json`](../../workflow/PathJoinNode/PathJoinNode.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/PathJoinNode/PathJoinNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `pathJoinNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
