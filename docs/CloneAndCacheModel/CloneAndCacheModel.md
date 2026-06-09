# Clone Model Node

![alt text](/imgs/CloneAndCacheModel/CloneAndCacheModel.png)  

## 1.1 Overview

Clones a model from pre-stored templates in the pyromind environment into the workspace cache. Models are already available in the environment, so cloning is very fast. The cloned model can be used by downstream training or inference nodes.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| model | STRING | Yes | Model identifier. Select from the dynamic list of available model templates in the pyromind environment (e.g., `Qwen/Qwen3-0.6B`, `Qwen/Qwen3-8B`). The list is loaded from the template directory at runtime. |
| target_path | STRING | Yes | Target directory in workspace to clone the model into. Default: `/workspace/models/` Options: /workspace/models/ |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| model_path | MODEL | Reference to the cloned model in workspace cache, passable to downstream training or inference nodes that accept a model input. |

## 1.4 Workflow JSON Definition

See [`workflow/CloneModel/CloneModel.json`](../../workflow/CloneModel/CloneModel.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/CloneModel/CloneModel.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `cloneAndCacheModel` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |

```bash
python -m pyromind_sdk.test_run_workflow_cli workflow/CloneModel/CloneModel.json --pretty
```

Example output:

```json
{
  "task_id": "4879",
  "task_name": "clonemodel",
  "status": "success",
  "error_message": null,
  "nodes": [
    {
      "node_key": "#1",
      "node_id": 18889,
      "node_type": "CloneAndCacheModel",
      "label": "",
      "start_at": "2026-06-09 03:32:14",
      "end_at": "2026-06-09 03:32:23",
      "duration": "0:00:09",
      "input": {
        "model": "Qwen/Qwen3-1.7B",
        "target_path": "/workspace/models/"
      },
      "output": {
        "model_path": "/workspace/models/Qwen/Qwen3-1.7B"
      },
      "raw": {}
    }
  ]
}
```
