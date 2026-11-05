# 自定义节点与插件

本目录用于在 PyroMind 平台上注册**自定义工作流节点**，以及提供训练/评估流程所需的**指标与奖励函数插件**。部署后，节点代码会同步到 Pod 内的 `/workspace/nodes/`，并通过 reload API 热加载。

## 目录结构

```
nodes/
├── install.sh                  # 部署脚本：复制文件并调用 reload API
├── InferenceConfig.yaml        # 模型服务配置节点定义
├── RolloutConfig.yaml          # 并发与任务选择配置节点定义
├── minisweBenchmark.yaml       # 单条/多条 SWE-bench 评测节点定义
├── custom_py_script/
│   ├── inference_config.py     # 打包 endpoint、model_name、api_key
│   ├── rollout_config.py       # 打包 works、num_tasks、start_index
│   └── coding_eval/
│       ├── eval_benchmark.py   # 推理 → 评分 → ATIF-v1.8 的节点入口
│       ├── run_harness.py      # 对已生成的预测补丁运行官方评分
│       ├── finish_evaluation.py # 不调用推理：评分或读取已有报告，再导出 ATIF
│       ├── atif_export.py      # 原始交互轨迹转换与 Harbor 格式校验
│       ├── requirements.txt   # 评测环境依赖（Python 3.12+）
│       ├── docker_ctx_prep.py  # Docker CLI 与 docker-rt 启动准备
│       ├── sandbox_tracking.py # 本次沙箱的命名、ID 记录与 Agent Docker 入口
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

每个节点对应一个 `*.yaml` 文件，放在 `nodes/` 根目录。示例见 `minisweBenchmark.yaml`：

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

在 `custom_py_script/`（或任意子目录）中实现入口函数。函数参数对应 YAML 中的 **input** 参数，返回值 `dict` 的 key 对应 **output** 参数。

`inference_config` 节点集中填写模型服务配置：`endpoint` 和 `model_name` 必填，`api_key` 选填。`endpoint` 可连接现有 Inference 节点输出，也可手动填写完整 API 基础地址；`model_name` 填写服务端模型 ID；`api_key` 无需鉴权时留空，开启鉴权时填写真实密钥。该节点只把三个字段打包为 JSON 字符串，通过 `inference_config` 输出端口传递。

将这个输出连接到 `minisweBenchmark` 的必填 `inference_config` 输入端口。`minisweBenchmark` 的入口 `eval_benchmark()` 读取配置后继续执行推理、评分和 ATIF 导出，保留基本 URL 格式检查。原来直接连接到 `minisweBenchmark.endpoint` 的连线需要改接到 `inference_config.endpoint`：

`rollout_config` 节点集中填写推理并发数和任务范围：`works` 必填，`num_tasks` 默认 `1`，`start_index` 默认 `0`。三个字段打包为 JSON 字符串，通过 `rollout_config` 输出端口连接到 `minisweBenchmark` 的同名必填输入；评测节点不再单独接收这三个字段。

```text
Inference.endpoint → inference_config.endpoint
inference_config.inference_config → minisweBenchmark.inference_config
rollout_config.rollout_config → minisweBenchmark.rollout_config
```

`pyromind_api_key` 仍在 `minisweBenchmark` 中填写，是 docker-rt 使用的 PyroMind 平台密钥，与模型端点密钥分开。集群固定为 `us-west-1#pre`，节点不提供 `cluster` 输入。`minisweBenchmark` 的 `inference_config`、`rollout_config`、`pyromind_api_key`、`output_dir` 均为必填。必填字段的空值检查交由平台处理，`rollout_config.works` 请填写大于零的整数。YAML 中必填输入排在选填输入前。

节点使用现有 `mini-extra swebench` 推理调用，通过任务数量和起始位置设置 `--slice`，然后用 SWE-bench 官方 harness 对所有补丁评分，并从各任务的实际交互轨迹生成、校验 ATIF-v1.8。原始 `preds.json` 只作为中间产物。详细约定见 `custom_py_script/coding_eval/ATIF_OUTPUT.md`。

`endpoint` 填写服务提供的完整 API 基础地址，例如 `https://服务域名/inference/服务ID/v1` 或 `https://服务域名/compatible-mode/v1`。节点仅清理首尾空格和末尾斜杠，检查基本 HTTP(S) URL 格式，不会自动添加 `/v1`，也不限制路径必须以 `/v1` 结尾，推理客户端直接使用此地址。不要填写 `/chat/completions` 等具体接口地址，也不要把密钥放在 URL 查询参数中。

节点不请求 `/models`，不自动发现、匹配或改写模型名称。`model_name` 直接传给推理客户端并记录到 ATIF 元数据，因此需要填写服务端实际接受的模型 ID，例如服务以 `--served-model-name default` 启动时填写 `default`。无需手动额外添加 `openai/` 前缀。模型名称、鉴权和服务连通性问题由实际推理请求返回。输入必填状态的界面变化需重新加载节点定义。

`inference_config.api_key` 留空时，传入空密钥并覆盖继承环境中的 `OPENAI_API_KEY`。填写了密钥时，推理使用该密钥。开启鉴权的服务仍必须填写正确密钥。

以下参数在 `rollout_config` 节点中填写：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `num_tasks` | `1` | 本次运行的任务数量，必须为正整数 |
| `start_index` | `0` | 从任务集哪个位置开始，必须为非负整数 |
| `works` | 必填 | 推理并发 worker 数；同时用于评分并发上限，实际评分并发不超过任务数 |

例如 `num_tasks=10, start_index=0, works=2` 表示选择前 10 条任务（`--slice 0:10`），并发上限为 2。`start_index=10` 则选择后面的第 11～20 条。实际数量受数据集剩余任务数限制；没有选中任务或没有有效预测时会报错。

当实际产物为 1 条任务时，`output_file_path` 仍直接指向 ATIF JSON。多条时，它指向 `manifest.json` 索引，索引中的 `tasks[].output_file_path` 才是每条任务的 ATIF-v1.8 文件路径。索引本身不是 ATIF 文档。更改节点 YAML 后需 reload 才会在平台出现新的输入参数。

注意：`python_code` 路径需与 Pod 内实际路径一致，通常为 `/workspace/nodes/...`。

### 3. 添加新节点

1. 在 `custom_py_script/` 下新增 Python 文件并实现入口函数
2. 在 `nodes/` 根目录新增对应的 `YourNode.yaml`
3. 运行 `./install.sh` 部署并 reload

### minisweBenchmark 的环境与离线验证

minisweBenchmark 的 Harbor 校验依赖 Python 3.12+；项目其他 SDK 示例的最低版本仍为 Python 3.10。请在节点实际使用的 `python3` 环境中安装依赖，或将 YAML 的 `python_command` 指向相应解释器：

```bash
python3.12 -m pip install -e . -r nodes/custom_py_script/coding_eval/requirements.txt
```

SDK 已固定为 `0.1.15`，提供本节点需要的 `docker-rt --sock/--pid-file` 功能；旧的 `0.1.9` 没有 `docker-rt` 子命令。可用 `python3.12 -m pyromind_sdk.cli docker-rt --help` 检查命令能力，该命令不会启动 daemon。

工具调用依赖固定为 `litellm[mcp]==1.106.6`。该版本即使处理普通 bash function tool，也会导入 MCP handler；仅安装基础 LiteLLM 可能在第一次请求前报 `No module named 'mcp'`。节点会在创建沙箱前导入同一 handler，缺少依赖时立即提示安装本目录的 requirements。对于当前工作区的 uv 环境，使用 `uv pip install --python .venv/bin/python -r nodes/custom_py_script/coding_eval/requirements.txt` 更新依赖；更新的是 minisweBenchmark 使用的解释器，而非模型服务容器。

在仓库根目录使用已有的推理产物验证转换，不启动模型、Docker 或评分程序。将下列路径和模型名称替换为实际值，预测文件同目录下需有 `<task_id>/<task_id>.traj.json`：

```bash
python3.12 nodes/custom_py_script/coding_eval/atif_export.py \
  /path/to/runs/preds.json \
  /path/to/output/trajectory.atif.json \
  --model-name your-served-model
```

此命令仅转换已有文件；未提供评分报告时，`final_metrics.extra.benchmark.status` 为 `not_run`，不生成虚假成绩。可通过 `--grading-report path/to/benchmark.json` 传入评分汇总；多任务使用 `--task-id` 选择对应结果，单任务自动选择唯一预测任务。也支持包含匹配 `task_id` 的旧版单任务标准化结果。

### 不重新推理，完成评分与 ATIF 导出

`finish_evaluation.py` 提供两个入口，均不调用推理或启动 docker-rt。两种方式都会先校验所有原始轨迹，再创建独立输出目录，生成每条任务的 ATIF 与评分汇总 `benchmark.json`。多任务另生成 `manifest.json`。

`benchmark.json` 在单任务和多任务时统一只包含 `summary` 和 `tasks`。`summary` 包含 `total_tasks`、`resolved_tasks`、`mean_score`；`tasks` 以任务 ID 为键，每条结果仅保留 `status`、`resolved`、`score`。

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
├── sandbox-containers/       # 每个容器一个 <容器名>.cid，记录实际创建的 ID
├── runs/
│   ├── docker-agent          # 带运行 ID 命名并通过 --cidfile 记录 Agent 容器的入口
│   ├── preds.json
│   └── <task_id>/<task_id>.traj.json
├── verified/                 # harness 日志、汇总报告和任务测试详情
├── benchmark.json            # 统一的 summary 和 tasks，任务仅含 status/resolved/score
├── trajectory.atif.json      # 单任务时 output_file_path 指向这里
├── trajectories/             # 多任务时每条任务一个 <task_id>.atif.json
└── manifest.json             # 多任务时 output_file_path 指向此索引
```

评分默认使用与节点相同的解释器，可通过 `HARNESS_PYTHON` 指定另一个可执行解释器路径。评分子进程使用本次运行的 Docker socket，超时为 4 小时；Docker API 默认超时提高到 300 秒。超时会终止本次 verifier 进程组，并尝试清理名称匹配该任务和 run ID 的评分容器。测试未通过会得到 `score: 0.0`；harness 错误、基础设施失败、轨迹缺失或格式校验失败会使节点报错并保留文件。

每次节点运行创建私有 `/tmp/pyromind-eval-*/docker.sock`、独立 PID 文件及 Docker 配置目录。独立 daemon 不代表远程沙箱列表隔离，因此收尾清理不通过全量容器列表判断归属。Agent 容器名称包含本次 run ID，Docker CLI 在创建后、启动前通过 `--cidfile` 记录 ID；harness 同样在创建评分容器后立即记录 ID。各容器使用独立文件，支持多 worker 并发写入。

节点在 `finally` 中只读取本次 `sandbox-containers/*.cid`，逐个检查完整 ID 和实际容器名称是否与记录及 run ID 一致，然后尝试删除容器及匿名卷，最后停止自己启动的 daemon。已经删除的容器直接跳过，归属不匹配或记录损坏时保留容器并写入 `cleanup.log`、发出警告。没有清单时不自动扫描删除其他容器，旧运行的遗留沙箱也不会自动接管。节点不接管共享 `/tmp/docker-rt.sock`，不执行全局容器或镜像 prune。没有本次运行的 PID 文件时，不调用 SDK 的进程扫描回退。实际远程沙箱清理效果仍需在真实环境验收。

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
