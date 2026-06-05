# Info Display (Middleware) 节点

![alt text](/imgs/ShowInfoNode/ShowInfoNode.png)  

## {{section}} 功能概述

Show Info 节点：获取上一个节点的执行结果，并发送到middleware pod
    
    参数说明：
    - previous_output: 上一个节点的输出值（通过{{previous_output}}占位符，会被替换为{{inputs.parameters.previous_output}}）
    - status: 输出状态文件路径（通过{{status}}占位符，会被替换为/tmp/status.txt）
    
    Middleware URL说明：
    - 使用完整DNS名称：k8s-sandbox-middleware-service.default.svc.cluster.local:80
    - 这样可以跨namespace访问（workflow在用户namespace，middleware在default namespace）
    - 直接发送POST请求到：http://k8s-sandbox-middleware-service.default.svc.cluster.local:80/api/v1/show-info

## {{section}} 输入类型

| 参数 | 数据类型 | 必填 | 描述 |
|------|---------|------|------|
| previous_output | * | 是 | 任意类型。默认值：- |
## {{section}} 输出类型

| 参数 | 数据类型 | 描述 |
|------|---------|------|
| status | STRING | 字符串 |

## {{section}} Workflow JSON 定义

完整 workflow 定义见 [`workflow/ShowInfoNode/ShowInfoNode.json`](../../workflow/ShowInfoNode/ShowInfoNode.json)。

## {{section}} 运行 Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/ShowInfoNode/ShowInfoNode.json [options]
```

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `--name` | `showInfoNode` | 任务名称 |
| `--output` | - | 输出结果文件 |
| `--poll-interval` | 5 | 轮询间隔（秒） |
| `--timeout` | 600 | 最大等待时间（秒） |
| `--pretty` | false | 美化 JSON 输出 |
| `--max-retries` | 0 | API 请求最大重试次数 |
| `-h, --help` | - | 显示帮助信息 |
