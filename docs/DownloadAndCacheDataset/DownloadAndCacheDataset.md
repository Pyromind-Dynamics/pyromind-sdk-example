# Download Dataset Node

![alt text](/imgs/DownloadAndCacheDataset/DownloadAndCacheDataset.png)  

## 1.1 Overview

下载并缓存数据集

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| dataset_name | STRING | Yes | String value. Default: `openai/gsm8k` |
| cache_dir | PATH | Yes | File system path. Default: `/workspace/datasets/openai/gsm8k` |
| download_source | STRING | Yes | String value. Default: `huggingface` Options: huggingface, modelscope |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| dataset_path | STRING | String value |

## 1.4 Workflow JSON Definition

See [`workflow/DownloadAndCacheDataset/DownloadAndCacheDataset.json`](../../workflow/DownloadAndCacheDataset/DownloadAndCacheDataset.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DownloadAndCacheDataset/DownloadAndCacheDataset.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `downloadAndCacheDataset` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
