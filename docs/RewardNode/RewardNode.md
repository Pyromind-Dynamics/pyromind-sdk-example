# Reward (Inference) Node

![alt text](/imgs/RewardNode/RewardNode.png)  

## {{section}} Overview

奖励函数计算节点

## {{section}} Input

| Parameter | Data Type | Required | Description |
|-----------|-----------|----------|-------------|
| reward_config | STRING | Yes | String value. Default: `configs/reward.yaml` |
| port | INT | Yes | Integer value. Default: `3000` |
| gpu_count | INT | Yes | Integer value. Default: `1` |
| gpu_product | STRING | Yes | String value. Default: `NVIDIA-H100-NVL` Options: NVIDIA-H100-NVL, NVIDIA-L40S, NVIDIA-H200, NVIDIA-B200, NVIDIA-H100-80GB-HBM3 |
| environment | ENV | No | Environment variable name. Default: - |
## {{section}} Output

| Parameter | Data Type | Description |
|-----------|-----------|-------------|
| endpoint | STRING | String value |

## {{section}} Workflow JSON Definition

See [`workflow/RewardNode/RewardNode.json`](../../workflow/RewardNode/RewardNode.json) for the full workflow definition.

## {{section}} Running the Workflow

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/RewardNode/RewardNode.json [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--name` | `rewardNode` | Task name |
| `--output` | - | Output results file |
| `--poll-interval` | 5 | Poll interval in seconds |
| `--timeout` | 600 | Max wait time in seconds |
| `--pretty` | false | Pretty-print JSON output |
| `--max-retries` | 0 | Max retries for API requests |
| `-h, --help` | - | Show help message |
