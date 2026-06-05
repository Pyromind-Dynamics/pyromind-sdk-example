# Info Display (Middleware) Node

![alt text](/imgs/ShowInfoNode/ShowInfoNode.png)  

## {{section}} Overview

Show Info 节点：获取上一个节点的执行结果，并发送到middleware pod
    
    参数说明：
    - previous_output: 上一个节点的输出值（通过{{previous_output}}占位符，会被替换为{{inputs.parameters.previous_output}}）
    - status: 输出状态文件路径（通过{{status}}占位符，会被替换为/tmp/status.txt）
    
    Middleware URL说明：
    - 使用完整DNS名称：k8s-sandbox-middleware-service.default.svc.cluster.local:80
    - 这样可以跨namespace访问（workflow在用户namespace，middleware在default namespace）
    - 直接发送POST请求到：http://k8s-sandbox-middleware-service.default.svc.cluster.local:80/api/v1/show-info

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| previous_output | * | Yes | Any type. Default: - |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| status | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/ShowInfoNode/ShowInfoNode.json`](../../workflow/ShowInfoNode/ShowInfoNode.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ShowInfoNode/ShowInfoNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `showInfoNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
