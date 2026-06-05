# SFT Model Config Builder Node

![alt text](/imgs/SFTModelConfigBuilderNode/SFTModelConfigBuilderNode.png)  

## {{section}} Overview

Build SFT model config YAML string.

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| model_name | STRING | No | String value. Default: `Qwen/Qwen3-VL-2B-Instruct` |
| model_type | STRING | No | String value. Default: `auto` |
| lora_rank | INT | No | Integer value. Default: `8` |
| full_finetune | BOOLEAN | No | Boolean flag (true/false). Default: `False` |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| model_config | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/SFTModelConfigBuilderNode/SFTModelConfigBuilderNode.json`](../../workflow/SFTModelConfigBuilderNode/SFTModelConfigBuilderNode.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/SFTModelConfigBuilderNode/SFTModelConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `sFTModelConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
