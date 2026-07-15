# Node Input String Object Conversion Analysis

This document analyzes which node input parameters can be converted into a
structured `STRING` payload, similar to `dataset_config`.

## Conversion Rule

Good candidates are groups of scalar parameters that describe one coherent
business configuration. These can be serialized as YAML or JSON and passed as a
single `STRING` parameter.

Do not merge runtime resources, path selectors, environment injection, or
arbitrary typed payloads into ordinary business config objects.

## Structured Inputs and Source Output Nodes

The table below marks which node output should feed each common structured
`STRING` input. `Suggested new` means the current sheet does not expose a clear
builder output yet; it is a recommended future abstraction.

| Structured input | Source output node | Output field | Consumer examples |
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
| `accelerate_config` | `AccelerateConfigBuilderNode` | `accelerate_config` | Training nodes; special `ACCELERATE_CONFIG` type, not an ordinary business object |
| `wandb_config` | `WandbConfigBuilderNode` | `wandb_config` | `ModelTrainSFTNode`, `ModelTrainGRPONode`, `ModelTrainDPONode`, `ModelTrainOPDNode`; special `WANDB_CONFIG` type, not an ordinary business object |
| `label_config` | Suggested new | `label_config` | `DataPreprocessLabelNode` |
| `reasoning_config` | Suggested new | `reasoning_config` | `DataPreprocessReasoningNode` |
| `prompt_expand_config` | Suggested new | `prompt_expand_config` | `DataPreprocessPromptExpandNode` |
| `split_config` | Suggested new | `split_config` | `DataPreprocessSplitNode` |
| `merge_config` | Suggested new | `merge_config` | `DataPreprocessMergeNode` |
| `validation_config` | Suggested new | `validation_config` | `ModelValidateGRPODataloaderNode` |
| `eval_config` | Suggested new | `eval_config` | `ModelEvalApiNode` |
| `opd_config` | Suggested new | `opd_config` | `ModelTrainOPDNode` |

## Strong Candidates

These nodes already behave like config builders, or their parameters form a
single clear configuration domain.

| Node | Current fields | Suggested structured input | Source output |
| --- | --- | --- | --- |
| `TrainingConfigBuilderNode` | `num_epochs`, `batch_size`, `grad_accum`, `learning_rate`, `lr_scheduler_type`, `logging_steps`, `save_steps`, `save_total_limit`, `eval_steps`, `seed`, `resume_from_checkpoint`, `max_grad_norm` | `training_config: STRING` | This node outputs `training_config` |
| `GRPOTrainingExtraConfigBuilderNode` | `max_steps`, `num_generations`, `max_prompt_length`, `max_completion_length`, `temperature`, `enable_chord`, `enable_hint` | `grpo_extra_config: STRING` | This node outputs `grpo_extra_config` |
| `DatasetExtraConfigBuilderNode` | `train_max_samples`, `val_max_samples`, `sft_collator_entry`, `dpo_collator_entry`, `grpo_collator_entry`, `max_seq_length` | `dataset_extra_config: STRING` | This node outputs `dataset_extra_config` |
| `LoraConfigBuilderNode` | `lora_rank`, `lora_dropout`, `target_modules`, `exclude_modules` | `lora_config: STRING` | This node outputs `lora_config` |
| `ModelConfigBuilderNode` | `model_path`, `model_type` | `model_config: STRING` | This node outputs `model_config` |
| `RewardItemBuilderNode` | `entry`, `name`, `kwargs`, `weight` | `reward_item: STRING` | This node outputs `reward_item` |
| `RewardItemBuilderCustomNode` | `entry`, `name`, `kwargs`, `weight` | `reward_item: STRING` | This node outputs `reward_item` |
| `RewardConfigBuilderNode` | `reward_item_1`, `reward_item_2`, `reward_item_3`, `reward_item_4`, `reward_item_5`, `normalize` | `reward_config: STRING` | This node outputs `reward_config` |
| `MetricsConfigBuilderNode` | `entry`, `name` | `metrics_config: STRING` | This node outputs `metrics_config` |
| `MetricsConfigBuilderCustomNode` | `entry`, `name` | `metrics_config: STRING` | This node outputs `metrics_config` |
| `WandbConfigBuilderNode` | `wandb_api_key`, `wandb_project`, `wandb_name` | `wandb_config: WANDB_CONFIG` | This node outputs `wandb_config`, but it should not be expanded as an ordinary business object |

## Medium Candidates

These nodes can be partially converted. Keep file paths, API endpoints, and
credentials explicit. Convert only behavior/configuration fields.

| Node | Keep explicit | Suggested grouped fields | Suggested structured input | Source output |
| --- | --- | --- | --- | --- |
| `DataPreprocessLabelNode` | `input_path`, `output_path`, `api_base`, `model`, `api_key` | `system_prompt`, `format_lang`, `extract`, `max_tokens`, `thinking`, `limit`, `concurrency` | `label_config: STRING` | Suggested new builder or direct caller-provided config |
| `DataPreprocessReasoningNode` | `input_path`, `output_path`, `api_base`, `model`, `api_key` | `system_prompt`, `user_prompt`, `user_prompt_column`, `format_lang`, `max_tokens`, `thinking`, `limit`, `concurrency`, `gt_column`, `num_variations` | `reasoning_config: STRING` | Suggested new builder or direct caller-provided config |
| `DataPreprocessPromptExpandNode` | `input_path`, `output_path`, `api_base`, `model`, `api_key` | `user_prompt`, `user_prompt_column`, `format_lang`, `system_prompt`, `max_tokens`, `thinking`, `limit`, `concurrency`, `num_variations` | `prompt_expand_config: STRING` | Suggested new builder or direct caller-provided config |
| `DataPreprocessSplitNode` | `input_path`, `output_path` | `train_ratio`, `seed`, `shuffle` | `split_config: STRING` | Suggested new builder or direct caller-provided config |
| `DataPreprocessMergeNode` | `metadata_path`, `output_path`, `reasoning_path`, `base_prompt_file`, `prompt_augmentation_path`, `system_prompt_file` | `base_prompt`, `output_format`, `category_annotations`, `system_prompt`, `copy_columns`, `label_column`, `gt_column` | `merge_config: STRING` | Suggested new builder or direct caller-provided config |
| `ModelValidateGRPODataloaderNode` | `dataset_config` | `rollout_size`, `check_reasoning`, `limit`, `verbose`, `preview_html_path`, `reward_config` | `validation_config: STRING` | Suggested new builder or direct caller-provided config |
| `ModelEvalApiNode` | `endpoint`, `endpoint_api_key`, `endpoint_model`, `output_path`, `dataset_config`, `metrics_config` | `max_samples`, `max_tokens`, `temperature` | `eval_config: STRING` | Suggested new builder or direct caller-provided config |
| `ModelTrainOPDNode` | `output_path`, `dataset_config`, `training_config`, `model_config`, `teacher_model_config`, `wandb_config` | `lmbda`, `beta`, `temperature`, `max_new_tokens`, `seq_kd`, `thinking_as_input_ratio` | `opd_config: STRING` | Suggested new builder or direct caller-provided config |

## Not Recommended

These input types or parameter groups should stay explicit.

| Type or field group | Examples | Reason |
| --- | --- | --- |
| `*` arbitrary input | `SaveAnythingToFileNode.content`, `SleepNode.origin`, `AnythingToString.anything`, `ContentPreview.content` | Runtime value can be any type; object schema is not stable. |
| `ENV` | `VLLMInference.environment`, `Inference.environment`, `PathJoinNode.environment` | Environment injection is runtime metadata, not business config. |
| `PATH` | `LoadDataset.source_dir`, `DownloadAndCacheDataset.cache_dir` | Path inputs usually need file/folder selector behavior and storage validation. |
| Runtime resources | `port`, `gpu_count`, `gpu_product` | These belong to execution scheduling, not business payloads. |
| Credentials and endpoints | `api_base`, `api_key`, `endpoint_api_key` | Keep explicit for security, visibility, and connection reuse. |
| File paths | `input_path`, `output_path`, `metadata_path`, `reasoning_path`, `model_path`, `dataset_path` | These are data handles, not config fields; keeping them explicit improves workflow wiring. |

## Practical Recommendation

Use structured `STRING` inputs for reusable config objects:

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

For preprocessing nodes, prefer a hybrid interface:

- Keep paths, API endpoints, model names, and credentials as separate top-level inputs.
- Group behavior controls into a single structured config string.

For training and validation nodes, keep existing config strings as the main
interface and avoid expanding them back into dozens of top-level scalar inputs.
