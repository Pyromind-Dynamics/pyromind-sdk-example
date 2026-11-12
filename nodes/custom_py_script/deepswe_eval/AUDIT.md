# DeepSWE 接入核查

核查日期：2026-11-11（Asia/Shanghai）。范围：当前源代码、`/workspace/nodes` 已部署文件、任务集、两次已完成的真实评测，以及离线回归检查。

2026-11-12 更新：第 4 项已按用户选择改为 miniswe 的“先校验并转换轨迹、再评分”流程；第 2 项已移除程序自动暂存/提交，改由 Agent 自己选择文件并提交。其他发现仍保留，历史评测结果未重写。

2026-11-12 批量运行后的更新：针对 `deepswe-ea00b277de644db7992140b2577a1056` 的 12 题运行，已修复空文件上传适配、加载官方输出截断模板、取消固定 150 轮并读取任务时限、停止重复重试 HTTP 400，以及保留含异常的提交诊断。网络问题不能由当前 SDK 直接解决，已增加可选严格模式，在不支持隔离时拒绝开始；PyroMind 默认模式仍不保证断网。历史分数未修改，未自动重新评测。

## 结论

当前执行的确实是官方 DeepSWE v1.1 任务和验证器，可用于本地功能评测。运行方式经过 PyroMind 适配，与官方榜单环境有差异。两次真实结果的原始 reward、测试报告、汇总和 ATIF 一致，没有发现这两个结果被错误转换。

实现仍有统计边界和复现信息方面的问题，详见下方；单任务成功不能替代多任务真实运行验证。

## 已确认的证据

- 数据集来源：`https://github.com/datacurve-ai/deep-swe`；提交：`0b9fabbb63b9104d678fe965e1632f2dd9eaa2ea`；113 个任务；任务目录没有 Git 工作区修改。
- 两次任务均为 `abs-module-cache-flags`。存档任务 checksum 与当前官方任务目录一致：`0a963e654cad3aef3019f942a528fcae97571ef1652f58c5413129b268b8f1db`。
- 存档 `instruction.txt` 与官方任务内容一致，原始模型轨迹的首个用户消息包含该题目。
- 两次运行均创建不同的做题容器和验证容器，使用官方 task.toml 指定的 `-v1.1` 镜像。
- 日志中的 `/tests` 上传只发生在验证容器；做题容器仅收到 `/logs/agent` 上传。未发现将 `solution/` 上传给 Agent 的路径或调用。
- collect hook 导出已提交的 `base..HEAD` 补丁；验证日志确认实际应用了 `model.patch`，随后执行官方 `tests/test.sh`、`grader.py` 与隐藏测试。
- pyrodash：原始 reward=0，3/23 测试通过；DeepSeek：原始 reward=1，23/23 测试通过。两者与 `benchmark.json`、`trajectory.atif.json` 一致，均为正常提交后的评分，非基础设施错误记零分。
- 当前源代码与 `/workspace/nodes/custom_py_script/deepswe_eval` 中的 Python 文件逐字节一致。

## 发现与限制

### 1. 官方运行条件未完全复现

`pier_runtime.py` 的 PyroMind 分支只记录断网能力未验证，不强制任务要求的 no-network。平台 API 的资源比例限制还使 2 CPU / 8 GiB 映射为 4 CPU / 8 GiB。这些差异已写入运行元数据。

`run_agent.py` 使用宿主机 Mini agent、自定义 system prompt；原先固定 150 轮和 7000 秒，现已加载官方 `mini.yaml` 的模型 observation/format-error 模板及默认 step_limit=0，时限读取任务文件（当前官方任务为 10800 秒）。提示词、宿主机执行、资源与网络仍与官方条件有差异。

批量运行已确认能下载 GitHub 仓库，并出现读取外部评测资料的行为。因此该批结果不能作为断网条件下的成绩。严格模式 `DEEPSWE_REQUIRE_NETWORK_ISOLATION=1` 要求标准 Docker daemon，拒绝 PyroMind/docker-rt。当前机器没有运行中的标准 Docker，尚未完成真实断网验证；适配器没有获得对 PyroMind 网络的控制能力。

### 2. 自动提交收集了无关产物（已移除自动提交）

原先 `run_agent.py` 在 Agent 结束后执行 `git add -A` 并提交所有改动。已完成的 pyrodash 运行由此包含编译产物 `abs` 和备份文件 `evaluator/functions.go.bak`，补丁大小为 8,452,795 字节；DeepSeek 补丁为 25,392 字节。

2026-11-12 已删除程序的自动 `git add -A` 和兜底提交，提示 Agent 自己检查改动、选择必要文件并提交。程序只读记录初始/最终提交、提交文件列表、diff 统计和工作区状态到 `agent/submission.json`，不替 Agent 修改提交范围。未创建提交时保留警告，由官方 collect hook/验证器照常处理，不另设基础设施失败。Agent 自己提交的不相关文件仍可能被收集，因此不能保证补丁一定不含产物。历史成绩未修改。

### 3. 批量均分采用已评分任务作为分母

`eval_benchmark.py:export_results()` 的 `mean_score` 是有效评分任务上的均分。离线复现：选择 2 题，1 题通过、1 题沙箱异常，报告为 `mean_score=1.0`，但已解决任务占全部选择任务的比例是 1/2。

它是有条件均分，不能直接当作完整任务集合的通过率。建议另外输出评分覆盖率和 `resolved_tasks / total_tasks`，有基础设施异常时明确标记运行不完整。本次两次运行都没有此类异常，因而不受该问题影响。

### 4. 轨迹失败与评分失败混在同一计数中（已修复）

核查时，有效评分但轨迹缺失会保留任务 `status=completed`，同时计入 `failed_tasks`。离线复现单题：`total_tasks=1, scored_tasks=1, failed_tasks=1, resolved_tasks=1`。

按用户选择，现已统一为 miniswe 的处理顺序：评分前校验并保存 ATIF，失败则不启动验证器；环境/推理等已有异常保留原始阶段。最终导出复用已校验轨迹；旧运行离线导出遇到无效轨迹时也统一记为未评分失败。计数满足 `total_tasks = scored_tasks + failed_tasks`。最终写文件异常使批次报错，不追加重复失败。本次两条真实轨迹均有效，历史结果未修改。

### 5. 运行时版本信息不足以证明未来任务目录未被修改

当前目录已核实干净，但入口仅记录 Git HEAD，不主动拒绝本地修改。自定义 `DEEPSWE_TASKS` 也只做格式检查，并不证明属于官方任务集。建议运行前校验任务内容，并在结果里记录每题 checksum、依赖版本及执行器代码版本。

## 验证

2026-11-12 批量异常修复后的回归：项目环境相关检查为 70 passed、16 skipped；独立 Pier 环境 DeepSWE 检查为 37 passed、1 deselected，覆盖前者跳过的运行时用例。113 个任务格式预检通过。使用真实 Mini 模型格式化路径验证约 300 万字符的原始输出只以首尾各 5000 字符发送，完整 raw_output 保留；同一 HTTP 400 不重复重试。合成 Pier 双沙箱流程覆盖空补丁上传并由验证器返回 0，未手工覆盖评分。另覆盖提交号前置换行、无效/缺失诊断字段、任务时限传递以及严格网络模式拒绝不支持的后端。没有重新调用真实模型、创建远程资源或修改历史结果；未完成真实断网验证。

2026-11-12 移除自动提交后的回归：项目环境相关检查为 66 passed、12 skipped；独立 Pier 环境 DeepSWE 检查为 29 passed、1 deselected。使用真实 Mini agent 和模拟模型响应验证：Agent 明确提交的源码进入补丁，编译产物和 `.bak` 保留未提交；Agent 未提交时 HEAD 和暂存区不被程序改变，提交诊断与有效轨迹正常保存。未调用真实模型或创建远程资源。

2026-11-12 修改后的离线检查：项目环境中 DeepSWE、Mini 批量/并发及配置相关检查为 65 passed、12 skipped；独立 Pier 环境 DeepSWE 检查为 28 passed、1 deselected，覆盖项目环境跳过的运行时用例。113 个官方任务格式预检通过。覆盖轨迹缺失、损坏、任务 ID 不符、无模型回复、推理异常、沙箱启动异常和写入失败；确认无效轨迹不创建验证沙箱、有效轨迹先保存后验证，并保留独立容器和并发限制。未调用真实模型或创建远程资源。

以下为 2026-11-11 原核查时的检查记录：

- 项目环境相关检查：14 passed，6 skipped；6 项运行时检查在独立 Pier 环境覆盖。
- 独立 Pier 环境：7 passed，其中一项与项目环境重复，包含真实 Mini 序列化、两阶段并发、独立验证与补丁应用、平台资源映射。
- 已用合成结果复现上述两项统计边界行为。
- 数据集完整性、题目传递、实际创建的容器、补丁应用、原始 reward 与导出分数均按两次真实运行记录交叉核对。
- 本次核查没有重新进行模型推理，也没有重写历史评测成绩。

## 真实结果位置

- `/workspace/eval_results/deepswe-6806370c5c5d4b11a43c199bdb466dcc/`
- `/workspace/eval_results/deepswe-c918d79eb13e48998749cc0b972fc92f/`

2026-11-12 按用户要求取消做题总时限：Mini wall_time_limit_seconds=0、宿主机 agent 子进程 timeout=None、Pier agent_timeout_sec=None。任务集文件未修改，评分仍按原任务配置限时；当前做题预算不再等同于标准 3 小时预算。单条命令和单次模型请求继续使用 300 秒。回归检查：项目环境 22 passed、19 skipped；隔离 Pier 环境 40 passed、1 deselected，覆盖三层总时限关闭和评分时限保留。未运行真实远程评测。

2026-11-12 按用户要求设置做题轮数上限 step_limit=300，做题总时限保持关闭；此轮数为自定义运行参数。
