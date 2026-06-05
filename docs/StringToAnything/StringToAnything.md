# String to Anything Node

![alt text](/imgs/StringToAnything/StringToAnything.png)  

## {{section}} Overview


> **TODO**: Add overview description


## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| input_string | STRING | Yes | String value. Default: - |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| anything | * | Any type |

## {{section}} Workflow JSON Definition

See [`workflow/StringToAnything/StringToAnything.json`](../../workflow/StringToAnything/StringToAnything.json) for the full workflow definition.

## {{section}} Running the Workflow

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
