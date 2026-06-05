# Load Model Node

![alt text](/imgs/LoadModel/LoadModel.png)  

## {{section}} Overview

加载基础模型用于RL训练

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| model_path | STRING | Yes | String value. Default: `path/to/model` |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| model | MODEL | Model reference |

## {{section}} Workflow JSON Definition

See [`workflow/LoadModel/LoadModel.json`](../../workflow/LoadModel/LoadModel.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/LoadModel/LoadModel.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `loadModel` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
