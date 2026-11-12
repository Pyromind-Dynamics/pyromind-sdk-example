# String to Anything Node

![alt text](/imgs/StringToAnything/StringToAnything.png)  

## 1.1 Overview


Converts a string input into any output type.


## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| input_string | STRING | Yes | Input string. Default: empty string |
## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| anything | * | Any type |

## 1.4 Workflow JSON Definition

See [`workflow/StringToAnything/StringToAnything.json`](../../workflow/StringToAnything/StringToAnything.json) for the full workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/StringToAnything/StringToAnything.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `stringToAnything` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
