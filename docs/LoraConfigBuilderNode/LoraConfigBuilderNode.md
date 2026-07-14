# Lora Config Builder Node

![alt text](/imgs/LoraConfigBuilderNode/LoraConfigBuilderNode.png)

## 1.1 Overview

Builds the `lora_config` YAML string (rank, dropout, target modules). Pass to training nodes via the optional `lora_config` input.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| lora_rank | INT | No | LoRA rank. Default: `8` |
| lora_dropout | FLOAT | No | LoRA dropout rate. Default: `0.05` |
| target_modules | STRING | No | Comma-separated LoRA target module names. Default: `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj` |
| exclude_modules | STRING | No | Comma-separated modules to exclude from LoRA. Default: empty string |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| lora_config | STRING\|LORA_CONFIG | LoRA config YAML string from Lora Config Builder |
## 1.4 Workflow JSON Definition

See [`workflow/LoraConfigBuilderNode/LoraConfigBuilderNode.json`](../../workflow/LoraConfigBuilderNode/LoraConfigBuilderNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/LoraConfigBuilderNode/LoraConfigBuilderNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `loraConfigBuilderNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
