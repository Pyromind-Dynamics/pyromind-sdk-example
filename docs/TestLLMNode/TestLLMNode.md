# LLM Test Node

![alt text](/imgs/TestLLMNode/TestLLMNode.png)  

## 1.1 Overview

Test SGLang node: tests an SGLang endpoint.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| endpoint | STRING | Yes | String value. Default: `http://localhost:30000` |
| prompt | STRING | Yes | String value. Default: `Hello, how are you?` |
| max_tokens | INT | Yes | Integer value. Default: `100` |
| temperature | FLOAT | Yes | Floating point number. Default: `0.7` |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| result | STRING | String value |

## 1.4 Workflow JSON Definition

See [`workflow/TestLLMNode/TestLLMNode.json`](../../workflow/TestLLMNode/TestLLMNode.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/TestLLMNode/TestLLMNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `testLLMNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
