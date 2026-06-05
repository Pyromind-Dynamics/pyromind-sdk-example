# Grounding XML Generation Node

![alt text](/imgs/DataPreprocessGroundingXmlNode/DataPreprocessGroundingXmlNode.png)  

## {{section}} Overview

Run data_preprocess grounding-xml pipeline and emit output path.

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| image_dir | STRING | Yes | String value. Default: - |
| output_dir | STRING | Yes | String value. Default: - |
| api_base | STRING | Yes | String value. Default: - |
| model | STRING | Yes | String value. Default: - |
| api_key | STRING | Yes | String value. Default: - |
| system_prompt | STRING | No | String value. Default: - |
| max_tokens | INT | No | Integer value. Default: `2048` |
| thinking | BOOLEAN | No | Boolean flag (true/false). Default: `False` |
| concurrency | INT | No | Integer value. Default: `8` |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| result_output_path | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/DataPreprocessGroundingXmlNode/DataPreprocessGroundingXmlNode.json`](../../workflow/DataPreprocessGroundingXmlNode/DataPreprocessGroundingXmlNode.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/DataPreprocessGroundingXmlNode/DataPreprocessGroundingXmlNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `dataPreprocessGroundingXmlNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
