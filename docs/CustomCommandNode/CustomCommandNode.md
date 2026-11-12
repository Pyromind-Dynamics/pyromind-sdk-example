# Custom Command Node

![alt text](/imgs/CustomCommandNode/CustomCommandNode.png)

## 1.1 Overview

Run a custom shell command with configurable CPU, memory, and GPU resources. Command output is captured and returned as a string.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| command | STRING | Yes | Shell command to execute. Default: two lines, `echo "hello from custom command"` and `echo "param=[$param]"` |
| cpu | INT | Yes | CPU limit in cores (1–64). Default: 4 |
| memory | INT | Yes | Memory limit in GiB (1–256). Default: 32 |
| gpu_count | INT | Yes | Number of GPUs to request (1–8). Default: 1 |
| gpu_product | STRING | Yes | GPU product to request when gpu_count is greater than zero. Options: NVIDIA-H200, NVIDIA-H100-80GB-HBM3. (subject to actual GPUs available in the target environment) |
| param | STRING | No | Optional parameter passed to the shell command and referenced as `$param`. Default: param-value |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| result | STRING | Captured standard output and standard error from the command. |

## 1.4 Workflow JSON Definition

See [workflow/CustomCommandNode/CustomCommandNode.json](../../workflow/CustomCommandNode/CustomCommandNode.json) for a basic command example. The [CustomCommandGPUNode workflow](../../workflow/CustomCommandNode/CustomCommandGPUNode.json) requests one `NVIDIA-H20` GPU in `cn-east-1#pre` and runs `nvidia-smi --query-gpu=name --format=csv,noheader`; its `result` output contains the GPU model visible inside the container. The validation run returned `NVIDIA H20-3e`. Change `gpu_product` if that product is unavailable in the target cluster.

## 1.5 Running the Workflow

~~~bash
export PYROMIND_API_KEY=<your-api-key>
# Run the GPU model probe
python - <<'PY'
import json
import os
from pathlib import Path
from pyromind_sdk import PyroMindAPIClient
from pyromind_sdk.client.models import TrainingTaskCreateRequest

workflow = json.loads(Path("workflow/CustomCommandNode/CustomCommandGPUNode.json").read_text())
client = PyroMindAPIClient(
    api_key=os.environ["PYROMIND_API_KEY"],
    base_url="https://pre-api-cn-east-1.pyromind-asia.cn/api/v1/",
    cluster="cn-east-1#pre",
)
result = client.studio.create_and_wait(
    TrainingTaskCreateRequest(
        name="custom-gpu-type-check",
        workflow=workflow,
        out_id="custom-gpu-type-check",
    ),
    timeout=300,
    check_interval=3,
    export_node_outputs=True,
)
print(f"Status: {result['status']}")
print(result["nodes"][0]["output"]["result"])
PY
~~~
