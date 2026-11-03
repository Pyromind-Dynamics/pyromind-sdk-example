# 自定义节点与插件

本目录用于在 PyroMind 平台上注册**自定义工作流节点**，以及提供训练/评估流程所需的**指标与奖励函数插件**。部署后，节点代码会同步到 Pod 内的 `/workspace/nodes/`，并通过 reload API 热加载。

## 目录结构

```
nodes/
├── install.sh                  # 部署脚本：复制文件并调用 reload API
├── EvalBenchmark.yaml          # 单条/多条 SWE-bench 评测节点定义
├── custom_py_script/
│   └── coding_eval/
│       ├── eval_benchmark.py   # 推理 → 评分 → ATIF-v1.8 的节点入口
│       ├── run_harness.py      # 对已生成的预测补丁运行官方评分
│       ├── finish_evaluation.py # 不调用推理：评分或读取已有报告，再导出 ATIF
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

在 `custom_py_script/`（或任意子目录）中实现入口函数。函数参数对应 YAML 中的 **input** 参数，返回值 `dict` 的 key 对应 **output** 参数。`EvalBenchmark` 的入口为 `eval_benchmark()`。`model_name` 是可选的服务端模型 ID，留空时从服务查询；`api_key` 是可选的模型端点密钥，无需鉴权时可不填，开启鉴权时填写真实密钥。`pyromind_api_key` 是 docker-rt 使用的 PyroMind 平台密钥，仍为必填，与模型端点密钥分开；`cluster` 填写 SDK 集群代码（如 `cn-east-1`）。除 `model_name`、`api_key`、`num_tasks`、`start_index` 外，其余输入仍由 YAML 标为必填，并在入口校验；Python 函数保留了原有位置参数顺序。

节点使用现有 `mini-extra swebench` 推理调用，通过任务数量和起始位置设置 `--slice`，然后用 SWE-bench 官方 harness 对所有补丁评分，并从各任务的实际交互轨迹生成、校验 ATIF-v1.8。原始 `preds.json` 只作为中间产物。详细约定见 `custom_py_script/coding_eval/ATIF_OUTPUT.md`。

创建沙箱前，节点会用模型服务密钥读取同一 endpoint 的 `GET /v1/models`，检查服务连通性及模型 ID。Inference 节点输出的 `endpoint` 是服务地址，不单独包含模型名称。`model_name` 不传或留空时，服务返回唯一模型 ID 则自动使用；没有模型或有多个模型时会列出可用名称，要求明确选择。有填写值时，优先精确匹配 `data[].id`。例如只填写 `Qwen3.5-4B`，而服务唯一匹配的 ID 为 `/workspace/.root/models/Qwen3.5-4B` 时，会自动使用完整 ID，并将其记录到评测和 ATIF 元数据。不存在、歧义、鉴权失败、接口不可用或返回无效数据时，会在分配沙箱前报错；不会替换名称不相关的显式模型，也不会改写显式填写的完整 ID。无需手动额外添加 `openai/` 前缀。可选输入的界面变化需重新加载节点定义。

`api_key` 留空时，模型元数据查询不发送 Authorization 头；推理客户端内部使用无效的 `dummy` 占位值满足 OpenAI 客户端要求，并覆盖继承环境中的 `OPENAI_API_KEY`，不会借用已有的真实密钥。填写了密钥时，元数据查询和推理都使用该密钥。开启鉴权的服务仍必须填写正确密钥。

| 参数 | 默认值 | 说明 |
|---|---|---|
| `num_tasks` | `1` | 本次运行的任务数量，必须为正整数 |
| `start_index` | `0` | 从任务集哪个位置开始，必须为非负整数 |
| `num_of_sandbox` | 必填 | 推理并发 worker 数；同时用于评分并发上限，实际评分并发不超过任务数 |

例如 `num_tasks=10, start_index=0, num_of_sandbox=2` 表示选择前 10 条任务（`--slice 0:10`），并发上限为 2。`start_index=10` 则选择后面的第 11～20 条。实际数量受数据集剩余任务数限制；没有选中任务或没有有效预测时会报错。

当实际产物为 1 条任务时，`output_file_path` 仍直接指向 ATIF JSON。多条时，它指向 `manifest.json` 索引，索引中的 `tasks[].output_file_path` 才是每条任务的 ATIF-v1.8 文件路径。索引本身不是 ATIF 文档。更改节点 YAML 后需 reload 才会在平台出现新的输入参数。

注意：`python_code` 路径需与 Pod 内实际路径一致，通常为 `/workspace/nodes/...`。

### 3. 添加新节点

1. 在 `custom_py_script/` 下新增 Python 文件并实现入口函数
2. 在 `nodes/` 根目录新增对应的 `YourNode.yaml`
3. 运行 `./install.sh` 部署并 reload

### EvalBenchmark 的环境与离线验证

EvalBenchmark 的 Harbor 校验依赖 Python 3.12+；项目其他 SDK 示例的最低版本仍为 Python 3.10。请在节点实际使用的 `python3` 环境中安装依赖，或将 YAML 的 `python_command` 指向相应解释器：

```bash
python3.12 -m pip install -e . -r nodes/custom_py_script/coding_eval/requirements.txt
```

SDK 已固定为 `0.1.15`，提供本节点需要的 `docker-rt --sock/--pid-file` 功能；旧的 `0.1.9` 没有 `docker-rt` 子命令。可用 `python3.12 -m pyromind_sdk.cli docker-rt --help` 检查命令能力，该命令不会启动 daemon。

工具调用依赖固定为 `litellm[mcp]==1.106.6`。该版本即使处理普通 bash function tool，也会导入 MCP handler；仅安装基础 LiteLLM 可能在第一次请求前报 `No module named 'mcp'`。节点会在创建沙箱前导入同一 handler，缺少依赖时立即提示安装本目录的 requirements。对于当前工作区的 uv 环境，使用 `uv pip install --python .venv/bin/python -r nodes/custom_py_script/coding_eval/requirements.txt` 更新依赖；更新的是 EvalBenchmark 使用的解释器，而非模型服务容器。

在仓库根目录使用已有的推理产物验证转换，不启动模型、Docker 或评分程序。将下列路径和模型名称替换为实际值，预测文件同目录下需有 `<task_id>/<task_id>.traj.json`：

```bash
python3.12 nodes/custom_py_script/coding_eval/atif_export.py \
  /path/to/runs/preds.json \
  /path/to/output/trajectory.atif.json \
  --model-name your-served-model
```

此命令仅转换已有文件；未提供评分报告时，`final_metrics.extra.benchmark.status` 为 `not_run`，不生成虚假成绩。可通过 `--grading-report path/to/benchmark.json` 传入 `run_harness.read_grading_result()` 返回的标准化结果（包含匹配的 `task_id`），不是原始 harness 汇总报告。

### 不重新推理，完成评分与 ATIF 导出

`finish_evaluation.py` 提供两个入口，均不调用推理或启动 docker-rt。两种方式都会先校验所有原始轨迹，再创建独立输出目录，生成每条任务的 ATIF 与标准化评分 `benchmark.json`。多任务另生成 `manifest.json`。

读取已有 harness 报告（不连接 Docker，也不重新评分）：

```bash
python3.12 nodes/custom_py_script/coding_eval/finish_evaluation.py \
  /path/to/runs/preds.json \
  --model-name your-served-model \
  --output-dir /path/to/output \
  --grading-dir /path/to/verified \
  --grading-run-id original-harness-run-id
```

`--grading-run-id` 对应原始报告文件名中的 run ID。支持 harness 的嵌套任务报告，以及 PyroDash 整理后的 `verified/<task_id>/report.json`。

预测文件可包含多条任务；程序会逐条校验轨迹和报告，并为每条任务单独生成 ATIF。所有任务必须来自同一模型。轨迹缺失、报告缺失或任何任务的基础设施错误会使本次节点报错，原始文件与日志保留；正常测试未通过的任务仍导出，成绩为零。

使用已运行的 Docker daemon 对已有预测评分，再导出 ATIF：

```bash
python3.12 nodes/custom_py_script/coding_eval/finish_evaluation.py \
  /path/to/runs/preds.json \
  --model-name your-served-model \
  --output-dir /path/to/output \
  --docker-host unix:///path/to/existing/docker.sock \
  --workers 2
```

实际评分前会 ping Docker；连接不可用时直接报错，不开始下载数据集。CLI 最后输出 `{"output_file_path": ".../trajectory.atif.json"}`，多任务时该路径为 `.../manifest.json`。合成报告只能用于验证文件读取和导出，不能作为真实评测成绩。

实际运行时，每次创建一个独立目录：

```text
output_dir/eval-<uuid>/
├── docker-rt.log
├── docker-rt-state.json       # 本次 daemon 的 socket、PID 文件及状态，不含密钥
├── docker-config/            # 本次运行独立的 Docker CLI 配置
├── runs/
│   ├── preds.json
│   └── <task_id>/<task_id>.traj.json
├── verified/                 # harness 日志、汇总报告和任务测试详情
├── benchmark.json            # 标准化的单条成绩或全部任务成绩与汇总
├── trajectory.atif.json      # 单任务时 output_file_path 指向这里
├── trajectories/             # 多任务时每条任务一个 <task_id>.atif.json
└── manifest.json             # 多任务时 output_file_path 指向此索引
```

评分默认使用与节点相同的解释器，可通过 `HARNESS_PYTHON` 指定另一个可执行解释器路径。评分子进程使用本次运行的 Docker socket，超时为 4 小时；Docker API 默认超时提高到 300 秒。超时会终止本次 verifier 进程组，并尝试清理名称匹配该任务和 run ID 的评分容器。测试未通过会得到 `score: 0.0`；harness 错误、基础设施失败、轨迹缺失或格式校验失败会使节点报错并保留文件。

每次节点运行创建私有 `/tmp/pyromind-eval-*/docker.sock`、独立 PID 文件及 Docker 配置目录。节点在 `finally` 中尝试停止自己启动的 daemon；不接管共享 `/tmp/docker-rt.sock`，不执行全局容器或镜像 prune。清理异常写入 `cleanup.log` 并发出警告。没有本次运行的 PID 文件时，不调用 SDK 的进程扫描回退。实际远程沙箱清理效果仍需在真实环境验收。

当前仅使用通用评分入口，区域兼容暂不在本次范围内。`PYROMIND_HARNESS_RUNNER` 仍可指定同环境中其他评分入口。真实 Pod 的镜像访问、评分执行及平台工作流尚待验证；当前工作区的解释器路径也需要在部署目标环境中确认。

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
