# Inference (VLLM) Node

![alt text](/imgs/VLLMInference/VLLMInference.png)

## 1.1 Overview

Run inference using vLLM, serving an OpenAI-compatible API endpoint.

## 1.2 Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| model_path | STRING | Yes | Model path reference |
| port | INT | Yes | Inference service port number. Default: `3000` |
| gpu_count | INT | Yes | Number of GPUs used by the inference service. Default: `1` |
| gpu_product | STRING | Yes | GPU type. Options: NVIDIA-H200, NVIDIA-H100-80GB-HBM3 (subject to actual GPUs available in the target environment) |
| environment | ENV | No | Environment variables |
| max_model_len | INT | No | Maximum model context length |
| startup_probe_max_duration | INT | No | Maximum startup probe duration (30–86400). Default: `1200` |

## 1.3 Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| endpoint | STRING | Endpoint of the inference service |

## 1.4 Workflow JSON Definition

See [`workflow/VLLMInference/VLLMInference.json`](../../workflow/VLLMInference/VLLMInference.json) for the workflow definition.

## 1.5 Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
export PYROMIND_CLUSTER=<your-cluster>
python -m pyromind_sdk.test_run_workflow_cli workflow/VLLMInference/VLLMInference.json --pretty
```
