# 名称含 config 但不应按普通对象展开的字段

本文基于飞书表 `WRoVgw` 当前 input/output 列、本地 workflow 示例，以及
`k8s_middleware` 系统节点定义，筛出“字段名里有 `config`，但实际不适合作为普通
业务对象展开”的字段。

## 结论

当前表格里，大多数 `_config` 字段确实是 YAML/JSON 对象字符串，例如
`dataset_config`、`training_config`、`model_config`、`lora_config`、
`reward_config`、`metrics_config`。

需要特别标注的例外主要有 4 类：

| 字段 | 出现位置 | 类型/形态 | 判断 | 处理建议 |
| --- | --- | --- | --- | --- |
| `wandb_config` | `ModelTrainSFTNode`, `ModelTrainGRPONode`, `ModelTrainDPONode`, `ModelTrainOPDNode`, `WandbConfigBuilderNode` | `WANDB_CONFIG` | 不是普通 `STRING` 对象。它承载 W&B 凭据和运行时环境配置，语义接近凭据/环境注入。 | 不建议按普通对象展开到飞书表；保留 `WANDB_CONFIG` 特殊类型，最多在 Builder 节点说明来源字段。 |
| `accelerate_config` | `AccelerateConfigBuilderNode` 输出；训练 workflow 中作为训练节点输入；`AccelerateGpuNode` 示例里也出现 | `ACCELERATE_CONFIG` | 不是普通业务对象。它是 Accelerate 启动/调度配置，包含执行环境、分布式、deepspeed 等运行配置。 | 保留 `ACCELERATE_CONFIG` 特殊类型；不要与 `dataset_config`、`training_config` 这类业务 payload 混为一类。 |
| `env_config` | 本地系统节点 `Environment` | `STRING`，默认值 `'{}'` | 不是业务对象，而是环境变量映射。字段名虽然叫 config，但语义是运行时 env map。 | 如进入文档，应标注为“环境变量映射 JSON”，不要归入训练/数据配置对象。 |
| `config` | workflow JSON 的 `data.config`、参数 schema 的 `config.enum/default` | JSON 元数据容器 | 不是节点 input/output 字段，只是 UI/workflow 内部存放节点参数值或参数 schema 的容器。 | 不写入节点 I/O 文档，不参与对象字段分析。 |

## 容易误判但实际仍是对象的字段

这些字段虽然目前表格里可能没有完全展开，或者类型不是 `STRING`，但语义上仍应按对象/对象片段理解。

| 字段 | 出现位置 | 说明 |
| --- | --- | --- |
| `teacher_model_config` | `ModelTrainOPDNode` | 这是 teacher 侧的 `model_config`，应复用 `ModelConfigBuilderNode.model_config` 的结构：`model_path`, `model_type`。当前表格没有展开字段，属于文档补充问题，不是非对象。 |
| `dataset_kind_config` | `DatasetConfigBuilderNode` 输入；三类 Dataset Kind Builder 输出 | 是 dataset 子配置片段。不同 Builder 当前输出字段可能不完全一致，仍然是对象片段。 |
| `dataset_extra_config` | `DatasetConfigBuilderNode` 输入；`DatasetExtraConfigBuilderNode` 输出 | 是 dataset 子配置片段。 |
| `reward_item_1` 到 `reward_item_5` | `RewardConfigBuilderNode` 输入；`reward_config` 内部字段 | 字段名不含 `_config`，但值是 `reward_item` YAML 片段，仍可展开为 `entry`, `name`, `kwargs`, `weight`。 |
| `metrics_json` / `metrics_yaml` | `ModelValidateGRPODataloaderNode`, `DatasetValidatorNode` 输出 | 字段名不叫 config，但输出内容里包含 `dataset_config`、`reward_config` 等对象字段，应该按结构化输出描述。 |

## 不应混入普通 config 对象的字段

以下字段本身不叫 `config`，但如果未来要把参数聚合成对象，也不建议塞进普通业务配置对象：

| 字段类型 | 示例 | 原因 |
| --- | --- | --- |
| 凭据 | `api_key`, `endpoint_api_key`, `wandb_api_key` | 安全边界和可见性要求更高，建议显式保留或走专用凭据类型。 |
| 服务端点 | `api_base`, `endpoint`, `endpoint_model` | 属于连接目标，不是业务 payload。 |
| 路径/数据句柄 | `input_path`, `output_path`, `model_path`, `dataset_path`, `preview_html_path` | 路径需要 storage 校验、选择器和连线语义，显式保留更清晰。 |
| 执行资源 | `port`, `gpu_count`, `gpu_product`, `environment` | 属于调度/运行时配置，不应并入训练或数据配置对象。 |

## 建议修正点

1. `teacher_model_config` 应在飞书表中展开为 `model_path`、`model_type`，来源标注为
   `ModelConfigBuilderNode.model_config`。
2. `wandb_config` 应继续显示为 `WANDB_CONFIG`，不要改成普通 `STRING` 对象。
3. `accelerate_config` 应继续显示为 `ACCELERATE_CONFIG`，并在说明中标注它是运行启动配置，不是业务对象。
4. 如果后续把系统节点 `Environment` 加入表格，`env_config` 应标注为环境变量映射 JSON，而不是普通业务配置对象。
