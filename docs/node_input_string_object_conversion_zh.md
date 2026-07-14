# 节点输入转结构化 String 对象分析

本文分析当前节点的 input 参数中，哪些适合转换为类似 `dataset_config` 的结构化
`STRING` 参数。

## 转换原则

适合转换的参数通常是一组同属一个业务配置域的标量字段，可以序列化为 YAML 或
JSON，并通过一个 `STRING` 参数传递。

不建议把运行资源、路径选择器、环境注入、任意类型输入等混入普通业务配置对象。

## 结构化输入与来源输出节点

下表标注了常见结构化 `STRING` 输入应由哪个节点输出。若来源为“建议新增”，表示当前表格里还没有明确的 Builder 输出节点，只是建议未来抽象。

| 结构化输入 | 来源输出节点 | 输出字段 | 消费节点示例 |
| --- | --- | --- | --- |
| `dataset_config` | `DatasetConfigBuilderNode` | `dataset_config` | `ModelTrainSFTNode`, `ModelTrainGRPONode`, `ModelTrainDPONode`, `ModelTrainOPDNode`, `ModelEvalApiNode`, `DatasetValidatorNode`, `ModelValidateGRPODataloaderNode` |
| `dataset_kind_config` | `DatasetConfigBuilderMessageNode` / `DatasetConfigBuilderVisionNode` / `DatasetConfigBuilderTextNode` | `dataset_kind_config` | `DatasetConfigBuilderNode` |
| `dataset_extra_config` | `DatasetExtraConfigBuilderNode` | `dataset_extra_config` | `DatasetConfigBuilderNode` |
| `training_config` | `TrainingConfigBuilderNode` | `training_config` | `ModelTrainSFTNode`, `ModelTrainGRPONode`, `ModelTrainDPONode`, `ModelTrainOPDNode` |
| `model_config` | `ModelConfigBuilderNode` | `model_config` | `ModelTrainSFTNode`, `ModelTrainGRPONode`, `ModelTrainDPONode`, `ModelTrainOPDNode` |
| `teacher_model_config` | `ModelConfigBuilderNode` | `model_config` | `ModelTrainOPDNode` |
| `lora_config` | `LoraConfigBuilderNode` | `lora_config` | `ModelTrainSFTNode`, `ModelTrainGRPONode`, `ModelTrainDPONode` |
| `reward_item` | `RewardItemBuilderNode` / `RewardItemBuilderCustomNode` | `reward_item` | `RewardConfigBuilderNode` |
| `reward_config` | `RewardConfigBuilderNode` | `reward_config` | `ModelTrainGRPONode`, `ModelValidateRewardNode`, `ModelValidateGRPODataloaderNode` |
| `metrics_config` | `MetricsConfigBuilderNode` / `MetricsConfigBuilderCustomNode` | `metrics_config` | `ModelEvalApiNode` |
| `grpo_extra_config` | `GRPOTrainingExtraConfigBuilderNode` | `grpo_extra_config` | `ModelTrainGRPONode` |
| `accelerate_config` | `AccelerateConfigBuilderNode` | `accelerate_config` | 训练节点（特殊类型 `ACCELERATE_CONFIG`，不按普通业务对象处理） |
| `wandb_config` | `WandbConfigBuilderNode` | `wandb_config` | `ModelTrainSFTNode`, `ModelTrainGRPONode`, `ModelTrainDPONode`, `ModelTrainOPDNode`（特殊类型 `WANDB_CONFIG`，不按普通业务对象处理） |
| `label_config` | 建议新增 | `label_config` | `DataPreprocessLabelNode` |
| `reasoning_config` | 建议新增 | `reasoning_config` | `DataPreprocessReasoningNode` |
| `prompt_expand_config` | 建议新增 | `prompt_expand_config` | `DataPreprocessPromptExpandNode` |
| `split_config` | 建议新增 | `split_config` | `DataPreprocessSplitNode` |
| `merge_config` | 建议新增 | `merge_config` | `DataPreprocessMergeNode` |
| `validation_config` | 建议新增 | `validation_config` | `ModelValidateGRPODataloaderNode` |
| `eval_config` | 建议新增 | `eval_config` | `ModelEvalApiNode` |
| `opd_config` | 建议新增 | `opd_config` | `ModelTrainOPDNode` |

## 强候选

这些节点本身就是配置构造节点，或者参数天然属于同一个配置对象。

| 节点 | 当前字段 | 建议转换为 | 对应输出 |
| --- | --- | --- | --- |
| `TrainingConfigBuilderNode` | `num_epochs`, `batch_size`, `grad_accum`, `learning_rate`, `lr_scheduler_type`, `logging_steps`, `save_steps`, `save_total_limit`, `eval_steps`, `seed`, `resume_from_checkpoint`, `max_grad_norm` | `training_config: STRING` | 本节点输出 `training_config` |
| `GRPOTrainingExtraConfigBuilderNode` | `max_steps`, `num_generations`, `max_prompt_length`, `max_completion_length`, `temperature`, `enable_chord`, `enable_hint` | `grpo_extra_config: STRING` | 本节点输出 `grpo_extra_config` |
| `DatasetExtraConfigBuilderNode` | `train_max_samples`, `val_max_samples`, `sft_collator_entry`, `dpo_collator_entry`, `grpo_collator_entry`, `max_seq_length` | `dataset_extra_config: STRING` | 本节点输出 `dataset_extra_config` |
| `LoraConfigBuilderNode` | `lora_rank`, `lora_dropout`, `target_modules`, `exclude_modules` | `lora_config: STRING` | 本节点输出 `lora_config` |
| `ModelConfigBuilderNode` | `model_path`, `model_type` | `model_config: STRING` | 本节点输出 `model_config` |
| `RewardItemBuilderNode` | `entry`, `name`, `kwargs`, `weight` | `reward_item: STRING` | 本节点输出 `reward_item` |
| `RewardItemBuilderCustomNode` | `entry`, `name`, `kwargs`, `weight` | `reward_item: STRING` | 本节点输出 `reward_item` |
| `RewardConfigBuilderNode` | `reward_item_1`, `reward_item_2`, `reward_item_3`, `reward_item_4`, `reward_item_5`, `normalize` | `reward_config: STRING` | 本节点输出 `reward_config` |
| `MetricsConfigBuilderNode` | `entry`, `name` | `metrics_config: STRING` | 本节点输出 `metrics_config` |
| `MetricsConfigBuilderCustomNode` | `entry`, `name` | `metrics_config: STRING` | 本节点输出 `metrics_config` |
| `WandbConfigBuilderNode` | `wandb_api_key`, `wandb_project`, `wandb_name` | `wandb_config: WANDB_CONFIG` | 本节点输出 `wandb_config`，但不建议按普通业务对象展开 |

## 中等候选

这些节点可以做部分转换。建议保留路径、API 地址、凭据等顶层参数，只把行为控制类字段聚合为配置对象。

| 节点 | 建议保留为顶层参数 | 建议聚合字段 | 建议转换为 | 对应输出 |
| --- | --- | --- | --- | --- |
| `DataPreprocessLabelNode` | `input_path`, `output_path`, `api_base`, `model`, `api_key` | `system_prompt`, `format_lang`, `extract`, `max_tokens`, `thinking`, `limit`, `concurrency` | `label_config: STRING` | 建议新增 Builder 或由调用方直接传入 |
| `DataPreprocessReasoningNode` | `input_path`, `output_path`, `api_base`, `model`, `api_key` | `system_prompt`, `user_prompt`, `user_prompt_column`, `format_lang`, `max_tokens`, `thinking`, `limit`, `concurrency`, `gt_column`, `num_variations` | `reasoning_config: STRING` | 建议新增 Builder 或由调用方直接传入 |
| `DataPreprocessPromptExpandNode` | `input_path`, `output_path`, `api_base`, `model`, `api_key` | `user_prompt`, `user_prompt_column`, `format_lang`, `system_prompt`, `max_tokens`, `thinking`, `limit`, `concurrency`, `num_variations` | `prompt_expand_config: STRING` | 建议新增 Builder 或由调用方直接传入 |
| `DataPreprocessSplitNode` | `input_path`, `output_path` | `train_ratio`, `seed`, `shuffle` | `split_config: STRING` | 建议新增 Builder 或由调用方直接传入 |
| `DataPreprocessMergeNode` | `metadata_path`, `output_path`, `reasoning_path`, `base_prompt_file`, `prompt_augmentation_path`, `system_prompt_file` | `base_prompt`, `output_format`, `category_annotations`, `system_prompt`, `copy_columns`, `label_column`, `gt_column` | `merge_config: STRING` | 建议新增 Builder 或由调用方直接传入 |
| `ModelValidateGRPODataloaderNode` | `dataset_config` | `rollout_size`, `check_reasoning`, `limit`, `verbose`, `preview_html_path`, `reward_config` | `validation_config: STRING` | 建议新增 Builder 或由调用方直接传入 |
| `ModelEvalApiNode` | `endpoint`, `endpoint_api_key`, `endpoint_model`, `output_path`, `dataset_config`, `metrics_config` | `max_samples`, `max_tokens`, `temperature` | `eval_config: STRING` | 建议新增 Builder 或由调用方直接传入 |
| `ModelTrainOPDNode` | `output_path`, `dataset_config`, `training_config`, `model_config`, `teacher_model_config`, `wandb_config` | `lmbda`, `beta`, `temperature`, `max_new_tokens`, `seq_kd`, `thinking_as_input_ratio` | `opd_config: STRING` | 建议新增 Builder 或由调用方直接传入 |

## 不建议转换

以下类型或字段组建议继续保持显式参数。

| 类型或字段组 | 示例 | 原因 |
| --- | --- | --- |
| `*` 任意类型输入 | `SaveAnythingToFileNode.content`, `SleepNode.origin`, `AnythingToString.anything`, `ContentPreview.content` | 运行时值可能是任意类型，结构不稳定，不适合固定对象 schema。 |
| `ENV` | `VLLMInference.environment`, `Inference.environment`, `PathJoinNode.environment` | 环境注入属于运行时元数据，不是业务配置。 |
| `PATH` | `LoadDataset.source_dir`, `DownloadAndCacheDataset.cache_dir` | 路径输入通常需要文件/目录选择器能力和 storage 校验。 |
| 运行资源参数 | `port`, `gpu_count`, `gpu_product` | 属于执行调度配置，不应塞进业务 payload。 |
| 凭据与端点 | `api_base`, `api_key`, `endpoint_api_key` | 建议显式保留，便于安全控制、可见性和连接复用。 |
| 文件/数据路径 | `input_path`, `output_path`, `metadata_path`, `reasoning_path`, `model_path`, `dataset_path` | 这些是数据句柄，不是配置字段；显式保留更利于 workflow 连线。 |

## 实际建议

优先使用结构化 `STRING` 表达可复用配置对象：

- `dataset_config`
- `dataset_kind_config`
- `dataset_extra_config`
- `training_config`
- `model_config`
- `lora_config`
- `reward_item`
- `reward_config`
- `metrics_config`
- `grpo_extra_config`

对于数据预处理节点，建议采用混合接口：

- 路径、API 地址、模型名、凭据继续保持顶层参数。
- 行为控制项聚合为一个结构化配置字符串。

对于训练和校验节点，建议继续以已有 config string 为主接口，避免重新展开成大量顶层标量参数。
