#!/usr/bin/env python3
"""Generate docs/ and docs_zh/ markdown from /workspace/nodes/*.yaml definitions."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

import yaml

NODES_DIR = Path("/workspace/nodes")
ROOT = Path(__file__).resolve().parents[1]
DOCS_EN = ROOT / "docs"
DOCS_ZH = ROOT / "docs_zh"
SKIP = {"zhaona_test"}

# Optional richer overview text keyed by node name.
OVERVIEWS_EN: dict[str, str] = {
    "DatasetConfigBuilderNode": (
        "Builds the base `dataset_config` YAML string for SFT/GRPO/DPO training. "
        "Combine with a **Dataset Kind Config Builder** node (Vision / Text / Messages) "
        "and **Dataset Extra Config Builder** to supply `dataset_kind_config` and "
        "`dataset_extra_config` inputs."
    ),
    "DatasetConfigBuilderVisionNode": (
        "Builds the `dataset_kind_config` YAML fragment for vision datasets "
        "(image + text fields). Connect its output to `DatasetConfigBuilderNode.dataset_kind_config`."
    ),
    "DatasetConfigBuilderTextNode": (
        "Builds the `dataset_kind_config` YAML fragment for text-only datasets. "
        "Connect its output to `DatasetConfigBuilderNode.dataset_kind_config`."
    ),
    "DatasetConfigBuilderMessageNode": (
        "Builds the `dataset_kind_config` YAML fragment for chat/messages datasets. "
        "Connect its output to `DatasetConfigBuilderNode.dataset_kind_config`."
    ),
    "DatasetExtraConfigBuilderNode": (
        "Builds the `dataset_extra_config` YAML fragment (collator entries, max samples, "
        "max sequence length). Connect its output to `DatasetConfigBuilderNode.dataset_extra_config`."
    ),
    "DatasetValidatorNode": (
        "Validates an assembled `dataset_config`, builds a dataloader preview, "
        "and outputs validation metrics plus an HTML preview path."
    ),
    "TrainingConfigBuilderNode": (
        "Assembles shared SFT/GRPO/DPO training hyperparameters into a `training_config` "
        "YAML string for downstream training nodes."
    ),
    "ModelConfigBuilderNode": (
        "Builds the `model_config` YAML string (model name and type). "
        "Use **Lora Config Builder** separately when LoRA fine-tuning is needed."
    ),
    "LoraConfigBuilderNode": (
        "Builds the `lora_config` YAML string (rank, dropout, target modules). "
        "Pass to training nodes via the optional `lora_config` input."
    ),
    "MetricsConfigBuilderNode": (
        "Builds a single metrics config YAML using a built-in evaluation entry "
        "(GSM8K, accuracy, BLEU, ROUGE-L)."
    ),
    "MetricsConfigBuilderCustomNode": (
        "Builds a metrics config YAML from a custom Python entry path "
        "(e.g. `/workspace/nodes/custom_entry/custom_metrics.py:compute_gsm8k`)."
    ),
    "RewardItemBuilderNode": (
        "Builds a single reward item YAML using a built-in reward entry. "
        "Non-empty `kwargs` enables factory mode."
    ),
    "RewardItemBuilderCustomNode": (
        "Builds a single reward item YAML from a custom Python entry path. "
        "Non-empty `kwargs` enables factory mode."
    ),
    "ModelEvalApiNode": (
        "Offline benchmark evaluation via an OpenAI-compatible Inference API. "
        "Loads a dataset, batch-calls the endpoint, computes metrics, and writes a report."
    ),
    "ModelTrainOPDNode": (
        "Runs OPD (On-Policy Distillation / GKD) training with separate student and "
        "teacher `model_config` inputs. Returns the trained model output directory."
    ),
    "DatasetToJsonlNode": (
        "Converts a HuggingFace dataset directory to a JSONL file path."
    ),
}

OVERVIEWS_ZH: dict[str, str] = {
    "DatasetConfigBuilderNode": (
        "构建 SFT/GRPO/DPO 训练的基础 `dataset_config` YAML 字符串。"
        "需配合 **Dataset Kind Config Builder**（Vision / Text / Messages）和 "
        "**Dataset Extra Config Builder** 节点，分别提供 `dataset_kind_config` 与 "
        "`dataset_extra_config` 输入。"
    ),
    "DatasetConfigBuilderVisionNode": (
        "构建视觉数据集（图片 + 文本字段）的 `dataset_kind_config` YAML 片段。"
        "输出连接至 `DatasetConfigBuilderNode.dataset_kind_config`。"
    ),
    "DatasetConfigBuilderTextNode": (
        "构建纯文本数据集的 `dataset_kind_config` YAML 片段。"
        "输出连接至 `DatasetConfigBuilderNode.dataset_kind_config`。"
    ),
    "DatasetConfigBuilderMessageNode": (
        "构建对话/消息格式数据集的 `dataset_kind_config` YAML 片段。"
        "输出连接至 `DatasetConfigBuilderNode.dataset_kind_config`。"
    ),
    "DatasetExtraConfigBuilderNode": (
        "构建 `dataset_extra_config` YAML 片段（collator 入口、最大样本数、最大序列长度等）。"
        "输出连接至 `DatasetConfigBuilderNode.dataset_extra_config`。"
    ),
    "DatasetValidatorNode": (
        "校验已组装的 `dataset_config`，生成 dataloader 预览，"
        "并输出校验指标与 HTML 预览文件路径。"
    ),
    "TrainingConfigBuilderNode": (
        "将 SFT/GRPO/DPO 共享训练超参数组装为 `training_config` YAML 字符串，"
        "供下游训练节点使用。"
    ),
    "ModelConfigBuilderNode": (
        "构建 `model_config` YAML 字符串（模型名称与类型）。"
        "LoRA 微调请单独使用 **Lora Config Builder** 节点。"
    ),
    "LoraConfigBuilderNode": (
        "构建 `lora_config` YAML 字符串（rank、dropout、target modules 等）。"
        "通过训练节点的可选 `lora_config` 输入传入。"
    ),
    "MetricsConfigBuilderNode": (
        "使用内置评估入口（GSM8K、accuracy、BLEU、ROUGE-L）构建单条 metrics 配置 YAML。"
    ),
    "MetricsConfigBuilderCustomNode": (
        "从自定义 Python 入口路径构建 metrics 配置 YAML"
        "（例如 `/workspace/nodes/custom_entry/custom_metrics.py:compute_gsm8k`）。"
    ),
    "RewardItemBuilderNode": (
        "使用内置奖励函数入口构建单条 reward item YAML。"
        "非空 `kwargs` 时启用 factory 模式。"
    ),
    "RewardItemBuilderCustomNode": (
        "从自定义 Python 入口路径构建单条 reward item YAML。"
        "非空 `kwargs` 时启用 factory 模式。"
    ),
    "ModelEvalApiNode": (
        "通过 OpenAI 兼容 Inference API 进行离线基准评测。"
        "加载数据集、批量调用端点、计算指标并输出评测报告。"
    ),
    "ModelTrainOPDNode": (
        "运行 OPD（On-Policy Distillation / GKD）训练，"
        "需分别提供 student 与 teacher 的 `model_config`。返回训练输出目录。"
    ),
    "DatasetToJsonlNode": (
        "将 HuggingFace 数据集目录转换为 JSONL 文件路径。"
    ),
}

DISPLAY_TITLES_EN: dict[str, str] = {
    "DatasetConfigBuilderMessageNode": "Dataset Kind Config Builder (Messages)",
    "DatasetConfigBuilderTextNode": "Dataset Kind Config Builder (Text Only)",
    "DatasetConfigBuilderVisionNode": "Dataset Kind Config Builder (Vision)",
    "DatasetValidatorNode": "Dataset Validator",
    "MetricsConfigBuilderNode": "Metrics Config Builder (System Entry)",
    "MetricsConfigBuilderCustomNode": "Metrics Config Builder (Custom Entry)",
    "RewardItemBuilderNode": "Reward Item Builder (System Entry)",
    "RewardItemBuilderCustomNode": "Reward Item Builder (Custom Entry)",
    "ModelEvalApiNode": "Benchmark By API",
    "ModelTrainOPDNode": "OPD Training",
}

DISPLAY_TITLES_ZH: dict[str, str] = {
    "DatasetConfigBuilderMessageNode": "Dataset Kind Config Builder（Messages）",
    "DatasetConfigBuilderTextNode": "Dataset Kind Config Builder（纯文本）",
    "DatasetConfigBuilderVisionNode": "Dataset Kind Config Builder（Vision）",
    "DatasetValidatorNode": "Dataset Validator 数据集校验",
    "MetricsConfigBuilderNode": "Metrics Config Builder（系统入口）",
    "MetricsConfigBuilderCustomNode": "Metrics Config Builder（自定义入口）",
    "RewardItemBuilderNode": "Reward Item Builder（系统入口）",
    "RewardItemBuilderCustomNode": "Reward Item Builder（自定义入口）",
    "ModelEvalApiNode": "Benchmark By API 离线评测",
    "ModelTrainOPDNode": "OPD 训练",
}

DEPRECATED_DOCS = {
    "SFTDatasetConfigValidatorNode",
    "SFTModelConfigBuilderNode",
    "SFTTrainingConfigBuilderNode",
}

PARAM_DESC_EN: dict[str, str] = {
    "train_data_path": "Training data path",
    "val_data_path": "Validation data path",
    "dataset_kind_config": "Dataset kind config YAML from a Kind Config Builder node",
    "dataset_extra_config": "Dataset extra config YAML from Dataset Extra Config Builder",
    "dataset_config": "Assembled dataset configuration YAML string",
    "training_config": "Training config YAML string (`BaseTrainingConfig` fields)",
    "model_config": "Model config YAML string",
    "teacher_model_config": "Teacher model config YAML string (OPD/GKD)",
    "lora_config": "LoRA config YAML string from Lora Config Builder",
    "wandb_config": "W&B configuration object",
    "grpo_extra_config": "GRPO-only extra training config YAML",
    "reward_config": "Reward config YAML from Reward Config Builder",
    "metrics_config": "Metrics config YAML from Metrics Config Builder",
    "model_output_path": "Trained model output directory",
    "benchmark_output_path": "Benchmark evaluation report output path",
    "jsonl_path": "Output JSONL file path",
    "metrics_yaml": "Validation metrics as YAML string",
    "output_preview_path": "Generated HTML preview file path",
    "reward_item": "Single reward item YAML string",
    "metrics_config": "Single metrics config YAML string",
    "accelerate_config": "Accelerate launch configuration YAML",
    "wandb_api_key": "W&B API key",
    "wandb_project": "W&B project name",
    "wandb_name": "W&B run name",
    "endpoint": "OpenAI-compatible inference API base URL",
    "endpoint_api_key": "Inference API key",
    "endpoint_model": "Model name served by the inference endpoint",
    "output_path": "Output directory or file path",
    "thinking_as_input_ratio": "Ratio of chain-of-thought content included as input",
    "lmbda": "OPD lambda mixing coefficient",
    "beta": "OPD beta coefficient",
    "temperature": "Sampling temperature",
    "max_new_tokens": "Maximum new tokens for teacher generation (OPD)",
    "seq_kd": "Enable sequence-level knowledge distillation",
    "max_samples": "Maximum evaluation samples (0 = all)",
    "max_tokens": "Maximum tokens per API completion",
    "entry": "Python entry path (`module.py:function_name`)",
    "name": "Metric or reward item name",
    "kwargs": "YAML mapping of keyword arguments (non-empty enables factory mode)",
    "weight": "Weight multiplier in combined score",
    "normalize": "Normalize combined reward scores",
    "model_name": "HuggingFace model name or local path",
    "model_type": "Model architecture type (`auto`, `qwen3vl`, `qwen3.5`)",
    "lora_rank": "LoRA rank",
    "lora_dropout": "LoRA dropout rate",
    "target_modules": "Comma-separated LoRA target module names",
    "exclude_modules": "Comma-separated modules to exclude from LoRA",
    "dataset_path": "Input dataset directory path",
    "check_reasoning": "Validate reasoning fields in the dataset",
    "limit": "Max samples for validation preview (0 = no limit)",
    "verbose": "Print detailed validation logs",
    "preview_html_path": "HTML preview output path",
    "status": "Validation status string",
    "scores": "Validation scores as YAML/JSON string",
    "completions": "Optional completions JSON for reward validation",
    "zero_stage": "DeepSpeed ZeRO stage",
    "gpu_info": "GPU information string",
    "execution_result": "Command execution result",
    "execution_output": "Command stdout/stderr output",
    "message_output": "Status message",
    "loaded_file_path": "Path of the loaded file",
    "content": "Loaded file content",
    "read_bytes": "Number of bytes read",
    "saved_file_path": "Path of the saved file",
    "written_bytes": "Number of bytes written",
    "merged_model_path": "Path to merged full-weight model",
    "metrics_json": "Validation metrics JSON string",
    "result_output_path": "Pipeline output path",
    "reasoning_path": "Reasoning pipeline output path",
    "augmentation_path": "Prompt expansion output path",
    "train_output_path": "Train split output path",
    "val_output_path": "Validation split output path",
    "messages_field": "Messages field name",
    "rejected_field": "Rejected response / messages field name",
    "system_prompt_field": "System prompt field name",
    "user_prompt_field": "User prompt field name",
    "image_field": "Image field name",
    "assistant_response_field": "Assistant response / ground-truth field name",
    "train_max_samples": "Max training samples (0 = all)",
    "val_max_samples": "Max validation samples (0 = all)",
    "sft_collator_entry": "SFT collator entry (`module:function`)",
    "dpo_collator_entry": "DPO collator entry (`module:function`)",
    "grpo_collator_entry": "GRPO collator entry (`module:function`)",
    "max_seq_length": "Maximum sequence length",
    "num_epochs": "Number of training epochs",
    "batch_size": "Per-device batch size",
    "grad_accum": "Gradient accumulation steps",
    "learning_rate": "Optimizer learning rate",
    "lr_scheduler_type": "Learning rate scheduler type",
    "logging_steps": "Log every N steps",
    "save_steps": "Save checkpoint every N steps",
    "save_total_limit": "Maximum number of checkpoints to keep",
    "eval_steps": "Evaluate every N steps",
    "seed": "Random seed",
    "resume_from_checkpoint": "Checkpoint path to resume from",
    "max_grad_norm": "Maximum gradient norm for clipping",
    "max_steps": "Maximum training steps (GRPO extra)",
    "num_generations": "Generations per prompt (GRPO extra)",
    "max_prompt_length": "Maximum prompt length (GRPO extra)",
    "max_completion_length": "Maximum completion length (GRPO extra)",
    "enable_chord": "Enable CHORD algorithm (GRPO extra)",
    "enable_hint": "Enable hint mode (GRPO extra)",
    "reward_item_1": "Reward item YAML #1",
    "reward_item_2": "Reward item YAML #2",
    "reward_item_3": "Reward item YAML #3",
    "reward_item_4": "Reward item YAML #4",
    "reward_item_5": "Reward item YAML #5",
    "file_path": "File path to load or save",
    "content_to_save": "Content to write to file",
}

PARAM_DESC_ZH: dict[str, str] = {
    "train_data_path": "训练数据路径",
    "val_data_path": "验证数据路径",
    "dataset_kind_config": "来自 Kind Config Builder 节点的 dataset kind 配置 YAML",
    "dataset_extra_config": "来自 Dataset Extra Config Builder 节点的额外配置 YAML",
    "dataset_config": "已组装的数据集配置 YAML 字符串",
    "training_config": "训练配置 YAML 字符串（`BaseTrainingConfig` 字段）",
    "model_config": "模型配置 YAML 字符串",
    "teacher_model_config": "Teacher 模型配置 YAML 字符串（OPD/GKD）",
    "lora_config": "来自 Lora Config Builder 的 LoRA 配置 YAML",
    "wandb_config": "W&B 配置对象",
    "grpo_extra_config": "GRPO 专用额外训练配置 YAML",
    "reward_config": "来自 Reward Config Builder 的奖励配置 YAML",
    "metrics_config": "来自 Metrics Config Builder 的指标配置 YAML",
    "model_output_path": "训练输出模型目录",
    "benchmark_output_path": "基准评测报告输出路径",
    "jsonl_path": "输出 JSONL 文件路径",
    "metrics_yaml": "校验指标 YAML 字符串",
    "output_preview_path": "生成的 HTML 预览文件路径",
    "reward_item": "单条 reward item YAML 字符串",
    "accelerate_config": "Accelerate 启动配置 YAML",
    "wandb_api_key": "W&B API Key",
    "wandb_project": "W&B 项目名称",
    "wandb_name": "W&B Run 名称",
    "endpoint": "OpenAI 兼容推理 API 地址",
    "endpoint_api_key": "推理 API Key",
    "endpoint_model": "推理端点提供的模型名称",
    "output_path": "输出目录或文件路径",
    "thinking_as_input_ratio": "将思维链内容作为输入的比例",
    "lmbda": "OPD lambda 混合系数",
    "beta": "OPD beta 系数",
    "temperature": "采样温度",
    "max_new_tokens": "Teacher 生成的最大 token 数（OPD）",
    "seq_kd": "是否启用序列级知识蒸馏",
    "max_samples": "最大评测样本数（0 表示全部）",
    "max_tokens": "每次 API 调用的最大 token 数",
    "entry": "Python 入口路径（`module.py:function_name`）",
    "name": "指标或 reward item 名称",
    "kwargs": "关键字参数字典 YAML（非空时启用 factory 模式）",
    "weight": "组合得分中的权重系数",
    "normalize": "是否对组合奖励得分归一化",
    "model_name": "HuggingFace 模型名或本地路径",
    "model_type": "模型架构类型（`auto`、`qwen3vl`、`qwen3.5`）",
    "lora_rank": "LoRA rank",
    "lora_dropout": "LoRA dropout",
    "target_modules": "LoRA 目标模块（逗号分隔）",
    "exclude_modules": "LoRA 排除模块（逗号分隔）",
    "dataset_path": "输入数据集目录路径",
    "check_reasoning": "是否校验数据集中的 reasoning 字段",
    "limit": "校验预览的最大样本数（0 表示不限制）",
    "verbose": "是否输出详细校验日志",
    "preview_html_path": "HTML 预览输出路径",
    "status": "校验状态字符串",
    "scores": "校验得分的 YAML/JSON 字符串",
    "completions": "用于奖励校验的可选 completions JSON",
    "zero_stage": "DeepSpeed ZeRO stage",
    "gpu_info": "GPU 信息字符串",
    "execution_result": "命令执行结果",
    "execution_output": "命令 stdout/stderr 输出",
    "message_output": "状态消息",
    "loaded_file_path": "已加载文件路径",
    "content": "已加载文件内容",
    "read_bytes": "读取字节数",
    "saved_file_path": "已保存文件路径",
    "written_bytes": "写入字节数",
    "merged_model_path": "合并后全量模型路径",
    "metrics_json": "校验指标 JSON 字符串",
    "result_output_path": "流水线输出路径",
    "reasoning_path": "Reasoning 流水线输出路径",
    "augmentation_path": "Prompt 扩展输出路径",
    "train_output_path": "训练集划分输出路径",
    "val_output_path": "验证集划分输出路径",
    "messages_field": "messages 字段名",
    "rejected_field": "拒绝回复 / rejected messages 字段名",
    "system_prompt_field": "system prompt 字段名",
    "user_prompt_field": "user prompt 字段名",
    "image_field": "图片字段名",
    "assistant_response_field": "助手回复 / ground-truth 字段名",
    "train_max_samples": "最大训练样本数（0 表示全部）",
    "val_max_samples": "最大验证样本数（0 表示全部）",
    "sft_collator_entry": "SFT collator 入口（`module:function`）",
    "dpo_collator_entry": "DPO collator 入口（`module:function`）",
    "grpo_collator_entry": "GRPO collator 入口（`module:function`）",
    "max_seq_length": "最大序列长度",
    "num_epochs": "训练 epoch 数",
    "batch_size": "每设备 batch size",
    "grad_accum": "梯度累积步数",
    "learning_rate": "优化器学习率",
    "lr_scheduler_type": "学习率调度器类型",
    "logging_steps": "每 N 步记录日志",
    "save_steps": "每 N 步保存 checkpoint",
    "save_total_limit": "保留 checkpoint 的最大数量",
    "eval_steps": "每 N 步执行评估",
    "seed": "随机种子",
    "resume_from_checkpoint": "恢复训练的 checkpoint 路径",
    "max_grad_norm": "梯度裁剪最大范数",
    "max_steps": "最大训练步数（GRPO extra）",
    "num_generations": "每个 prompt 的生成数（GRPO extra）",
    "max_prompt_length": "最大 prompt 长度（GRPO extra）",
    "max_completion_length": "最大 completion 长度（GRPO extra）",
    "enable_chord": "是否启用 CHORD 算法（GRPO extra）",
    "enable_hint": "是否启用 hint 模式（GRPO extra）",
    "reward_item_1": "Reward item YAML #1",
    "reward_item_2": "Reward item YAML #2",
    "reward_item_3": "Reward item YAML #3",
    "reward_item_4": "Reward item YAML #4",
    "reward_item_5": "Reward item YAML #5",
    "file_path": "加载或保存的文件路径",
    "content_to_save": "写入文件的内容",
}


def _fmt_default(value, lang: str = "en") -> str:
    if value is None:
        return "-"
    if value == "":
        return "空字符串" if lang == "zh" else "empty string"
    if isinstance(value, bool):
        return "true" if value else "false"
    return f"`{value}`"


def _param_description(name: str, param: dict, lang: str) -> str:
    desc_map = PARAM_DESC_ZH if lang == "zh" else PARAM_DESC_EN
    base = desc_map.get(name, name.replace("_", " ").capitalize())
    enum_vals = param.get("config", {}).get("enum")
    if enum_vals:
        opts = ", ".join(f"`{v}`" for v in enum_vals)
        suffix = f"选项：{opts}" if lang == "zh" else f"Options: {opts}"
        return f"{base}。{suffix}" if lang == "zh" else f"{base}. {suffix}"
    default = param.get("default")
    if default is not None and param.get("required_type") != "required":
        d = _fmt_default(default, lang)
        return f"{base}。默认值：{d}" if lang == "zh" else f"{base}. Default: {d}"
    return base


def _load_node(yaml_path: Path) -> dict:
    with open(yaml_path) as f:
        return yaml.safe_load(f)


def _overview(node_name: str, data: dict, lang: str) -> str:
    custom = (OVERVIEWS_ZH if lang == "zh" else OVERVIEWS_EN).get(node_name)
    if custom:
        return custom
    desc = data.get("description") or ""
    if isinstance(desc, str):
        return " ".join(desc.split())
    return str(desc).strip()


def _title(node_name: str, data: dict, lang: str) -> str:
    titles = DISPLAY_TITLES_ZH if lang == "zh" else DISPLAY_TITLES_EN
    if node_name in titles:
        return titles[node_name]
    display = data.get("display_name") or node_name
    suffix = " 节点" if lang == "zh" and not str(display).endswith("节点") else ""
    en_suffix = " Node" if lang == "en" and not str(display).lower().endswith("node") else ""
    if lang == "zh":
        return f"{display}{suffix}"
    return f"{display}{en_suffix}"


def generate_doc(node_name: str, data: dict, lang: str) -> str:
    title = _title(node_name, data, lang)
    overview = _overview(node_name, data, lang)
    params = data.get("parameters") or []
    inputs = [p for p in params if p.get("type") == "input"]
    outputs = [p for p in params if p.get("type") == "output"]

    if lang == "zh":
        input_header = "## 1.2 输入类型\n\n| 参数 | 数据类型 | 必填 | 描述 |\n|------|---------|------|------|"
        output_header = "## 1.3 输出类型\n\n| 参数 | 数据类型 | 描述 |\n|------|---------|------|"
        overview_header = "## 1.1 功能概述"
        wf_header = "## 1.4 Workflow JSON 定义"
        run_header = "## 1.5 运行 Workflow"
        wf_text = (
            f"完整 workflow 定义见 [`workflow/{node_name}/{node_name}.json`]"
            f"(../../workflow/{node_name}/{node_name}.json)。"
        )
        opt_header = "| 选项 | 默认值 | 说明 |"
        req_yes, req_no = "是", "否"
    else:
        input_header = "## 1.2 Input\n\n| Parameter | Data Type | Required | Description |\n|-----------|-----------|----------|-------------|"
        output_header = "## 1.3 Output\n\n| Parameter | Data Type | Description |\n|-----------|-----------|-------------|"
        overview_header = "## 1.1 Overview"
        wf_header = "## 1.4 Workflow JSON Definition"
        run_header = "## 1.5 Running the Workflow"
        wf_text = (
            f"See [`workflow/{node_name}/{node_name}.json`]"
            f"(../../workflow/{node_name}/{node_name}.json) for the full workflow definition."
        )
        opt_header = "| Option | Default | Description |"
        req_yes, req_no = "Yes", "No"

    input_rows = []
    for p in inputs:
        req = req_yes if p.get("required_type") == "required" else req_no
        input_rows.append(
            f"| {p['name']} | {p['dtype']} | {req} | {_param_description(p['name'], p, lang)} |"
        )

    output_rows = [
        f"| {p['name']} | {p['dtype']} | {_param_description(p['name'], p, lang)} |"
        for p in outputs
    ]

    default_name = node_name[0].lower() + node_name[1:] if node_name else node_name
    lines = [
        f"# {title}",
        "",
        f"![alt text](/imgs/{node_name}/{node_name}.png)",
        "",
        overview_header,
        "",
        overview,
        "",
        input_header,
        *input_rows,
        "",
        output_header,
        *output_rows,
        "",
        wf_header,
        "",
        wf_text,
        "",
        run_header,
        "",
        "```bash",
        "export PYROMIND_API_KEY=<your-api-key>",
        f"python -m pyromind_sdk.test_run_workflow_cli workflow/{node_name}/{node_name}.json [options]",
        "```",
        "",
        opt_header,
        "|--------|---------|-------------|" if lang == "en" else "|------|--------|------|",
    ]
    if lang == "zh":
        lines.extend([
            f"| `--name` | `{default_name}` | 任务名称 |",
            "| `--output` | - | 输出结果文件 |",
            "| `--poll-interval` | 5 | 轮询间隔（秒） |",
            "| `--timeout` | 600 | 最大等待时间（秒） |",
            "| `--pretty` | false | 美化 JSON 输出 |",
            "| `--max-retries` | 0 | API 请求最大重试次数 |",
            "| `-h, --help` | - | 显示帮助信息 |",
        ])
    else:
        lines.extend([
            f"| `--name` | `{default_name}` | Task name |",
            "| `--output` | - | Output results file |",
            "| `--poll-interval` | 5 | Poll interval in seconds |",
            "| `--timeout` | 600 | Max wait time in seconds |",
            "| `--pretty` | false | Pretty-print JSON output |",
            "| `--max-retries` | 0 | Max retries for API requests |",
            "| `-h, --help` | - | Show help message |",
        ])
    return "\n".join(lines) + "\n"


def main() -> None:
    updated = []
    for yaml_path in sorted(NODES_DIR.glob("*.yaml")):
        if yaml_path.stem in SKIP:
            continue
        data = _load_node(yaml_path)
        node_name = data.get("name") or yaml_path.stem

        for lang, docs_dir in (("en", DOCS_EN), ("zh", DOCS_ZH)):
            out_dir = docs_dir / node_name
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / f"{node_name}.md"
            out_file.write_text(generate_doc(node_name, data, lang))
        updated.append(node_name)

    for deprecated in DEPRECATED_DOCS:
        for docs_dir in (DOCS_EN, DOCS_ZH):
            dep_dir = docs_dir / deprecated
            if dep_dir.exists():
                for f in dep_dir.iterdir():
                    f.unlink()
                dep_dir.rmdir()
                print(f"Removed deprecated docs: {docs_dir.name}/{deprecated}")

    print(f"Generated docs for {len(updated)} nodes:")
    for name in updated:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
