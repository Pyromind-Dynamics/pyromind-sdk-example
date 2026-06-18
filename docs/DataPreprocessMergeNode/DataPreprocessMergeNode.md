# Prompt & Reasoning Merge Node

![alt text](/imgs/DataPreprocessMergeNode/DataPreprocessMergeNode.png)

## 1.1 Overview

Merge reasoning/category/prompts into training data.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| metadata_path | STRING | Yes | - |
| output_path | STRING | Yes | Output directory path |
| reasoning_path | STRING | Yes | - |
| base_prompt | STRING | No | Default: `''` |
| output_format | STRING | No | Default: `jsonl` |
| base_prompt_file | STRING | No | Default: `''` |
| category_annotations | STRING | No | Default: `''` |
| prompt_augmentation_path | STRING | No | Default: `''` |
| system_prompt | STRING | No | Default: `''` |
| system_prompt_file | STRING | No | Default: `''` |
| copy_columns | STRING | No | Default: `''` |
| label_column | STRING | No | Default: `component_type` |
| gt_column | STRING | No | Default: `text` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| result_output_path | STRING | result_output_path |

## 1.4 Workflow JSON Definition

See [`workflow/DataPreprocessMergeNode/DataPreprocessMergeNode.json`](../../workflow/DataPreprocessMergeNode/DataPreprocessMergeNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DataPreprocessMergeNode/DataPreprocessMergeNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `dataPreprocessMergeNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
