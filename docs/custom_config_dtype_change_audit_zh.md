# 自定义节点 config 字段是否可改为多类型审计

目标：判断用户/共享自定义节点 YAML 中，名称包含 `config` 的参数是否适合把
`dtype` 从 `STRING` 改成 `STRING|对象`。

结论：不能全部改。普通 `STRING` 配置对象可以改，专用类型和运行时配置不要改。

## 可以改为 `STRING|对象`

这些字段当前是 `STRING`，且飞书表中已经能展开对象字段，适合在自定义节点 YAML 中
改成多类型：

| 字段 | 适用节点 |
| --- | --- |
| `dataset_config` | `ModelTrainGRPONode`, `ModelTrainSFTNode`, `ModelValidateGRPODataloaderNode`, `DatasetConfigBuilderNode`, `ModelTrainDPONode`, `ModelEvalApiNode`, `ModelTrainOPDNode`, `DatasetValidatorNode` |
| `dataset_kind_config` | `ModelTrainGRPONode`, `ModelTrainSFTNode`, `ModelValidateGRPODataloaderNode`, `DatasetConfigBuilderNode`, `ModelTrainDPONode`, `ModelEvalApiNode`, `ModelTrainOPDNode`, `DatasetValidatorNode`, `DatasetConfigBuilderMessageNode`, `DatasetConfigBuilderVisionNode`, `DatasetConfigBuilderTextNode` |
| `dataset_extra_config` | `ModelTrainGRPONode`, `ModelTrainSFTNode`, `ModelValidateGRPODataloaderNode`, `DatasetConfigBuilderNode`, `ModelTrainDPONode`, `ModelEvalApiNode`, `ModelTrainOPDNode`, `DatasetExtraConfigBuilderNode`, `DatasetValidatorNode` |
| `training_config` | `ModelTrainGRPONode`, `ModelTrainSFTNode`, `ModelTrainDPONode`, `ModelTrainOPDNode`, `TrainingConfigBuilderNode` |
| `model_config` | `ModelTrainGRPONode`, `ModelTrainSFTNode`, `ModelTrainDPONode`, `ModelTrainOPDNode`, `ModelConfigBuilderNode` |
| `teacher_model_config` | `ModelTrainOPDNode` |
| `lora_config` | `ModelTrainGRPONode`, `ModelTrainSFTNode`, `ModelTrainDPONode`, `LoraConfigBuilderNode` |
| `reward_config` | `ModelTrainGRPONode`, `ModelValidateRewardNode`, `ModelValidateGRPODataloaderNode`, `RewardConfigBuilderNode` |
| `grpo_extra_config` | `ModelTrainGRPONode`, `GRPOTrainingExtraConfigBuilderNode` |
| `metrics_config` | `ModelEvalApiNode`, `MetricsConfigBuilderNode`, `MetricsConfigBuilderCustomNode` |

推荐 YAML 写法：

```yaml
dtype: STRING|对象
```

如果 SDK 侧对象类型使用英文 token，则用：

```yaml
dtype: STRING|OBJECT
```

## 不建议改

这些字段虽然名字包含 `config`，但不是普通业务对象：

| 字段 | 适用节点 | 当前类型 | 原因 |
| --- | --- | --- | --- |
| `wandb_config` | `ModelTrainGRPONode`, `ModelTrainSFTNode`, `ModelTrainDPONode`, `ModelTrainOPDNode`, `WandbConfigBuilderNode` | `WANDB_CONFIG` | 专用凭据/运行环境配置类型，不应降级或混成普通对象类型。 |
| `accelerate_config` | `AccelerateConfigBuilderNode`，以及训练/Accelerate workflow 中的连接字段 | `ACCELERATE_CONFIG` | 专用启动/调度配置类型，不是业务 payload。 |

## 不需要直接改的嵌套字段

飞书表里有些输出对象内部也出现了 `dataset_config`、`dataset_kind_config`、
`dataset_extra_config`，例如：

- `DatasetValidatorNode.metrics_yaml`
- `ModelValidateGRPODataloaderNode.metrics_json`

这些是输出对象里的嵌套字段，不一定对应 YAML 顶层参数。真正需要改的是顶层参数
`metrics_yaml` / `metrics_json` 是否支持对象；不要把嵌套字段误认为独立 YAML 参数。

## 最小修改原则

只改用户/共享自定义节点 YAML 中的顶层 input/output 参数：

```yaml
parameters:
  - name: dataset_config
    type: input
    dtype: STRING|对象
```

不要改：

- `WANDB_CONFIG`
- `ACCELERATE_CONFIG`
- workflow JSON 里的内部 `data.config`
- 参数 schema 里的 `config.default` / `config.enum`
