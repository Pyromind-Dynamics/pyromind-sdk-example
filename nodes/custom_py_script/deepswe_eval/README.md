# deepsweBenchmark

连接现有 `inference_config` 和 `rollout_config`，通过 mini-swe-agent 2.4.6 做题，使用 Pier 0.3.1 的 DeepSWE 1.1 独立验证流程评分，返回 ATIF-v1.8 或多任务索引。

## 准备环境

在节点实际运行的机器上，从仓库根目录执行：

```bash
bash nodes/custom_py_script/deepswe_eval/setup.sh
```

脚本将 Pier 与 Mini agent 安装在 uv 独立工具环境，不改变现有 `minisweBenchmark` 的 Python 依赖。任务集默认位于 `/workspace/datasets/deep-swe/tasks`，固定提交为 `0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea`。每次评测记录实际的数据集提交。

可设置 `DEEPSWE_TASKS` 修改任务位置；自备 Python 环境可按 `requirements.txt` 安装依赖，再通过 `DEEPSWE_PYTHON` 指定解释器。节点使用的主解释器仍需安装 `../coding_eval/requirements.txt`，用于平台 SDK 和 Harbor ATIF-v1.8 校验。

只验证依赖与全部任务的格式，不调用模型或创建沙箱：

```bash
.venv/bin/python nodes/custom_py_script/deepswe_eval/eval_benchmark.py \
  --check --num-tasks 113
```

## 平台接线

先同步节点文件并调用平台 reload（已有部署脚本为 `nodes/install.sh`）。

```text
inference_config.inference_config ─┐
                                  ├→ deepsweBenchmark → output_file_path
rollout_config.rollout_config ─────┘
```

节点另需填写 `pyromind_api_key` 和 `output_dir`。两个配置节点保持原有字段：

| 配置 | 字段 | 说明 |
|---|---|---|
| inference_config | endpoint | 完整的模型 API 基础地址，支持 Chat Completions |
| inference_config | model_name | 服务端接受的模型 ID |
| inference_config | api_key | 模型服务密钥；无需认证时可留空 |
| rollout_config | inference_workers | 做题阶段并发数，正整数 |
| rollout_config | grading_workers | 验证阶段并发数，正整数 |
| rollout_config | num_tasks | 本次任务数，默认 1 |
| rollout_config | start_index | 按任务目录名排序后的起始位置，默认 0 |

首次测试将任务数和两个并发数都设为 `1`，起始位置设为 `0`。做题和评分使用不同沙箱；模型密钥只留在评测宿主机进程中，不传入任务沙箱。Agent 自己选择文件并提交代码，由官方 collect hook 生成 `base..HEAD` 补丁；验证器只接收补丁和隐藏测试，不读取参考解。

程序不再自动执行 `git add -A` 或兜底提交。提示词要求 Agent 检查改动、明确选择必要的源码/测试/资源文件并提交，避免将临时编译产物、缓存和备份文件纳入提交。结束时只读检查 Git 状态，将初始/最终提交、已提交文件列表、diff 统计和未提交文件列表记录到 `trials/<task>/agent/submission.json`；诊断记录失败只写警告，不改变评分。若 Agent 没有提交，程序会警告但不会替它提交，也不会人为标成环境失败；仍由官方 collect hook 和验证器处理。如果 HEAD 相对官方基准没有变化，收集到的就是空补丁。Agent 自己提交的二进制或备份文件仍会进入补丁，程序不按文件类型强行过滤。

## 命令行单任务测试

在本机设置 `PYROMIND_API_KEY`（平台密钥）和 `OPENAI_API_KEY`（模型服务密钥）后执行。API key 不作为命令行参数或持久化运行配置保存。

```bash
.venv/bin/python nodes/custom_py_script/deepswe_eval/eval_benchmark.py \
  --endpoint https://token-plan-cn-east-1.pyromind-asia.cn/v1 \
  --model-name pyrodash \
  --num-tasks 1 --start-index 0 \
  --inference-workers 1 --grading-workers 1 \
  --output-dir /workspace/eval_results
```

默认启动本次运行专用的 PyroMind docker-rt，集群与现有 Mini 节点一致，使用 `us-west-1#pre`。结束或异常时清理本次拥有的容器并关闭 daemon。也可通过 `DEEPSWE_DOCKER_HOST` 指定标准 Docker daemon；此时不创建或关闭 daemon，仅清理本次运行的容器。标准 Docker 模式需要 `/usr/local/bin/docker` 可执行。

## 输出

每次运行在 `output_dir/deepswe-<uuid>/` 下生成：

```text
run-config.json       无密钥的任务、模型地址、并发与数据集版本
pier.log              评测执行日志
pier-results.json     Pier 原始任务结果
benchmark.json        评分汇总、任务分数和异常原因
manifest.json         ATIF 文件索引（所有运行均生成）
trajectory.atif.json  单题有效轨迹
trajectories/         多题有效轨迹
trials/<task>/agent/  Mini 原始交互轨迹与日志
                     submission.json：提交记录、文件列表与未提交状态
trials/<task>/verifier/  reward.json、测试日志与报告
```

与现有 `minisweBenchmark` 一致：Agent 保存原始轨迹后，先校验并转换为 ATIF，保存到 `trials/<task>/agent/trajectory.atif.json`，成功后才创建独立验证沙箱评分。轨迹缺失、损坏或无法转换时跳过评分，记为 `failed`、`score=null`。原始轨迹中的模型/Agent 异常归为 `inference`；沙箱启动失败保留 `environment` 错误，不被后续的“轨迹缺失”覆盖。原始轨迹和日志保留用于排查。

`output_file_path` 在单题有有效轨迹时直接返回 ATIF 文件；多题或单题无有效轨迹时返回 `manifest.json`。正常未通过的任务记为 0，仍计入 `scored_tasks`；环境、模型调用、轨迹或验证异常计入 `failed_tasks`，分数为 `null`。同一道任务不会同时计入已评分和失败，`total_tasks = scored_tasks + failed_tasks`。均分只统计有效评分。最终导出复用评分前的 ATIF 并附加评分；最终文件写入失败会像 miniswe 一样报错，不将它追加为已评分任务的失败计数。离线导出旧运行时也先检查轨迹，无效轨迹对应的汇总分数为 `null`；不改写 Pier 原始结果。

## 网络与可比性

PyroMind 平台要求 CPU 与内存为每核 2 GiB。适配器按此比例向上分配，保留任务要求的最低 CPU 和内存，例如任务要求 `2 CPU / 8 GiB` 时申请 `4 CPU / 8 GiB`。做题和评分环境都使用此映射。任务集文件保持原样，原始需求与实际分配记录在 `trials/<task>/resources-agent.json`、`resources-verifier.json` 以及导出的 ATIF 元数据中。标准 Docker 模式直接使用任务指定的资源。

标准 Docker 模式对声明断网的任务使用 `--network none`。当前 PyroMind SDK 0.1.15 的 docker-rt 不执行这个网络设置；平台可能施加额外网络策略，但本适配器未验证，因此结果记录 `network_isolation=platform-managed-unverified`，用于本地评测，不等同于官方榜单环境。Agent 提示词及宿主机运行方式也与 Pier 默认的容器内 Agent 有差异。独立验证、官方测试和 collect hook 保留原有流程。

## 离线回归检查

```bash
.venv/bin/python -m pytest -q tests/test_deepswe_benchmark.py
~/.local/share/uv/tools/datacurve-pier/bin/python -m pytest -q \
  tests/test_deepswe_benchmark.py -k 'not node_loads'
```

第二条需要在独立运行环境额外安装 pytest。检查使用合成任务和模拟模型响应，不调用真实模型、读取参考解或创建远程资源。
