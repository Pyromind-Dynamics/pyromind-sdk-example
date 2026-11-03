# 自定义节点与插件

本目录用于在 PyroMind 平台上注册**自定义工作流节点**，以及提供训练/评估流程所需的**指标与奖励函数插件**。部署后，节点代码会同步到 Pod 内的 `/workspace/nodes/`，并通过 reload API 热加载。

## 目录结构

```
nodes/
├── install.sh                  # 部署脚本：复制文件并调用 reload API
├── EvalBenchmark.yaml          # 单任务 SWE-bench 评测节点定义
├── custom_py_script/
│   └── coding_eval/
│       ├── eval_benchmark.py   # 推理 → 评分 → ATIF-v1.8 的节点入口
│       ├── run_harness.py      # 对已生成的预测补丁运行官方评分
│       ├── atif_export.py      # 原始交互轨迹转换与 Harbor 格式校验
│       ├── requirements.txt   # 评测环境依赖（Python 3.12+）
│       ├── docker-ctx-prep.py  # Docker CLI 与 docker-rt 启动准备
│       ├── ATIF_OUTPUT.md      # ATIF-v1.8 输出约定
│       └── CHECKLIST.md        # 后续实现清单
└── custom_entry/
    ├── custom_metrics.py       # 评估指标插件
    └── custom_rewards.py       # GRPO 奖励函数插件
```

## 快速部署

在已挂载 `/workspace` 的运行环境中执行：

```bash
export PYROMIND_API_KEY=<your-api-key>
./install.sh
```

也可将 token 作为第一个参数传入：

```bash
./install.sh <your-api-key>
```

脚本会：

1. 将本目录内容（除 `install.sh` 外）同步到 `/workspace/nodes/`
2. 调用 `POST /api/v1/nodes/reload` 重新加载节点定义

可通过环境变量覆盖 reload 地址：

```bash
export PYROMIND_RELOAD_URL="https://pre-api.pyromind.ai/api/v1/nodes/reload?allow_delete=true&allow_recreate=true"
```

## 自定义工作流节点

### 1. 编写节点定义（YAML）

每个节点对应一个 `*.yaml` 文件，放在 `nodes/` 根目录。示例见 `EvalBenchmark.yaml`：

| 字段 | 说明 |
|------|------|
| `name` | 节点类型名，workflow 中引用 |
| `display_name` | 界面显示名称 |
| `description` | 节点描述 |
| `base_class` | 基类，如 `PodExecutionNode` |
| `python_code` | Pod 内 Python 文件绝对路径 |
| `function_name` | 入口函数名 |
| `python_command` | 解释器，如 `python3` |
| `parameters` | 输入/输出参数列表 |

`parameters` 中每个参数包含：

- `name`：参数名
- `dtype`：数据类型（如 `STRING`、`INT`、`BOOLEAN`）
- `type`：`input` 或 `output`
- `required_type`：输入是否必填（`required` / `optional`）

### 2. 编写 Python 实现

在 `custom_py_script/`（或任意子目录）中实现入口函数。函数参数对应 YAML 中的 **input** 参数，返回值 `dict` 的 key 对应 **output** 参数。`EvalBenchmark` 的入口为 `eval_benchmark(endpoint: str, model_name: str, api_key: str, pyromind_api_key: str, cluster: str, num_of_sandbox: int, output_dir: str)`。`model_name` 填写服务端模型 ID，`api_key` 填写模型端点密钥；无需鉴权的端点可填写 `dummy`。`pyromind_api_key` 是 docker-rt 使用的 PyroMind 平台密钥，与模型端点密钥分开；`cluster` 填写 SDK 集群代码（如 `cn-east-1`）。

节点保留现有 `mini-extra swebench --slice 0:1` 推理调用，然后使用 SWE-bench 官方 harness 对补丁评分，并从实际保存的交互轨迹生成、校验 ATIF-v1.8。`output_file_path` 返回最终 ATIF 文件路径，原始 `preds.json` 只作为中间产物。详细约定见 `custom_py_script/coding_eval/ATIF_OUTPUT.md`。

注意：`python_code` 路径需与 Pod 内实际路径一致，通常为 `/workspace/nodes/...`。

### 3. 添加新节点

1. 在 `custom_py_script/` 下新增 Python 文件并实现入口函数
2. 在 `nodes/` 根目录新增对应的 `YourNode.yaml`
3. 运行 `./install.sh` 部署并 reload

### EvalBenchmark 的环境与离线验证

EvalBenchmark 的 Harbor 校验依赖 Python 3.12+；项目其他 SDK 示例的最低版本仍为 Python 3.10。请在节点实际使用的 `python3` 环境中安装依赖，或将 YAML 的 `python_command` 指向相应解释器：

```bash
python3.12 -m pip install -r nodes/custom_py_script/coding_eval/requirements.txt
```

在仓库根目录使用已有的推理产物验证转换，不启动模型、Docker 或评分程序。将下列路径和模型名称替换为实际值，预测文件同目录下需有 `<task_id>/<task_id>.traj.json`：

```bash
python3.12 nodes/custom_py_script/coding_eval/atif_export.py \
  /path/to/runs/preds.json \
  /path/to/output/trajectory.atif.json \
  --model-name your-served-model
```

此命令仅转换已有文件；未提供评分报告时，`final_metrics.extra.benchmark.status` 为 `not_run`，不生成虚假成绩。可通过 `--grading-report path/to/benchmark.json` 传入 `run_harness.read_grading_result()` 返回的标准化结果（包含匹配的 `task_id`），不是原始 harness 汇总报告。

实际运行时，每次创建一个独立目录：

```text
output_dir/eval-<uuid>/
├── docker-rt.log
├── runs/
│   ├── preds.json
│   └── <task_id>/<task_id>.traj.json
├── verified/                 # harness 日志、汇总报告和任务测试详情
└── trajectory.atif.json      # output_file_path 指向这里
```

评分默认使用与节点相同的解释器，可通过 `HARNESS_PYTHON` 指定另一个可执行解释器路径。评分子进程沿用 Docker socket，超时为 4 小时；Docker API 默认超时提高到 300 秒。测试未通过会得到 `score: 0.0`；harness 错误、基础设施失败、轨迹缺失或格式校验失败会使节点报错并保留文件。

内置评分入口只包含通用 Docker 超时适配，没有复制 PyroDash 的上海镜像、GitHub 缓存及 docker-rt 特殊兼容补丁。需要原有区域适配时，在同一运行环境部署相应脚本及其 `shanghai/` 目录，再设置 `PYROMIND_HARNESS_RUNNER` 指向该 `run_harness.py`；其 `CLUSTER=shanghai` 等环境变量与节点的 SDK 集群参数分别配置。真实 Pod 中的镜像访问、区域兼容性和端到端运行仍需验证。Docker 准备逻辑保留现状，使用共享 `/tmp/docker-rt.sock`；独立输出目录不代表 Docker daemon 也已隔离。

## 自定义评估指标（custom_metrics.py）

供 `train/eval_model_api.py` 的 `--metrics-entry` 使用。每个指标导出独立可调用函数，通过 `path/to/file.py:function_name` 加载，并配合 `--metrics-name` 指定聚合字段名。

当前内置：

| 函数 | 说明 |
|------|------|
| `compute_gsm8k` | GSM8K 数值答案准确率，从 `####`、`\boxed{}`、`<answer>` 等格式提取最终数字并比较 |

函数签名约定：

```python
def compute_gsm8k(
    gt_text: str,
    pred_text: str,
    sample: dict,
    *,
    metrics_name: str | None = None,
) -> dict | None:
    ...
```

本地快速验证：

```bash
python custom_entry/custom_metrics.py
```

## 自定义奖励函数（custom_rewards.py）

供 GRPO 训练流程使用。数据集中 `gt` 与模型输出格式为：

```
<think>...</think>

<answer>X</answer>
```

当前内置：

| 函数 | 说明 |
|------|------|
| `thinking_reward` | 检查最后一个 thinking 块是否非空且长度超过阈值（默认 20 字符） |
| `answer_reward` | 比较预测答案与 `ground_truth` 中的 `<answer>` 标签内容 |

在 workflow 中可通过 [RewardItemBuilderNode](../docs_zh/RewardItemBuilderNode/RewardItemBuilderNode.md) 配置 `entry` 指向插件路径，例如：

```
/workspace/nodes/custom_entry/custom_rewards.py:answer_reward
```

本地快速验证：

```bash
python custom_entry/custom_rewards.py
```

## 与系统节点的关系

本仓库根目录的 `docs/`、`workflow/` 描述的是**平台内置节点**的文档与测试用例；`nodes/` 目录则是**用户自定义扩展**，二者相互独立。自定义节点部署后，可在 workflow JSON 中像内置节点一样引用其 `name` 字段。

## 常见问题

**Q: reload 失败怎么办？**

检查 `PYROMIND_API_KEY` 是否有效，以及 `PYROMIND_RELOAD_URL` 是否指向正确的环境（pre / prod）。

**Q: 节点执行报找不到 Python 文件？**

确认 YAML 中 `python_code` 路径与 Pod 内 `/workspace/nodes/` 下的实际路径一致，且已执行 `./install.sh` 完成同步。

**Q: 如何调试奖励/指标函数？**

直接在本机运行对应 `.py` 文件的 `__main__` 块，或在 Pod 内用相同路径手动 import 测试。
