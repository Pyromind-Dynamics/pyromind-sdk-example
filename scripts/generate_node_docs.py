#!/usr/bin/env python3
"""Generate docs/ and docs_zh/ markdown from node YAML definitions."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

NODES_DIR = Path("/workspace/nodes")
DOCS_EN = Path(__file__).resolve().parents[1] / "docs"
DOCS_ZH = Path(__file__).resolve().parents[1] / "docs_zh"

DISPLAY_NAME_EN: dict[str, str] = {
    "DatasetConfigBuilderVisionNode": "Dataset Kind Config Builder (Vision)",
    "DatasetConfigBuilderTextNode": "Dataset Kind Config Builder (Text Only)",
    "DatasetConfigBuilderMessageNode": "Dataset Kind Config Builder (Messages)",
    "DatasetValidatorNode": "Dataset Validator",
    "MetricsConfigBuilderNode": "Metrics Config Builder (System Entry)",
    "MetricsConfigBuilderCustomNode": "Metrics Config Builder (Custom Entry)",
    "RewardItemBuilderNode": "Reward Item Builder (System Entry)",
    "RewardItemBuilderCustomNode": "Reward Item Builder (Custom Entry)",
    "ModelEvalApiNode": "Benchmark By Api",
    "ModelTrainOPDNode": "OPD Training",
}

OVERVIEW_EN: dict[str, str] = {
    "DatasetConfigBuilderNode": (
        "Builds a dataset configuration YAML string for SFT/GRPO/DPO training. "
        "Combines `train_data_path`, optional `dataset_kind_config` (from Vision/Text/Messages builders), "
        "and optional `dataset_extra_config` (from Dataset Extra Config Builder)."
    ),
    "DatasetConfigBuilderVisionNode": (
        "Builds vision dataloader kind config YAML. Connect output to `dataset_kind_config` on Dataset Config Builder."
    ),
    "DatasetConfigBuilderTextNode": (
        "Builds text-only dataloader kind config YAML. Connect output to `dataset_kind_config` on Dataset Config Builder."
    ),
    "DatasetConfigBuilderMessageNode": (
        "Builds messages-format dataloader kind config YAML. Connect output to `dataset_kind_config` on Dataset Config Builder."
    ),
    "DatasetExtraConfigBuilderNode": (
        "Builds dataset extra config YAML (collator entries, max_seq_length, sample limits). "
        "Connect output to `dataset_extra_config` on Dataset Config Builder."
    ),
    "TrainingConfigBuilderNode": (
        "Assembles shared SFT/GRPO/DPO training hyperparameters into a `training_config` YAML string."
    ),
    "ModelConfigBuilderNode": "Builds model config YAML string (`model_path`, `model_type`).",
    "LoraConfigBuilderNode": "Builds LoRA config YAML string for optional LoRA training.",
    "ModelTrainSFTNode": "Run SFT training and return the output model directory.",
    "ModelTrainDPONode": "Run DPO training and return the output model directory.",
    "ModelTrainGRPONode": (
        "Main GRPO training node using SFT-aligned YAML: dataset_config, training_config, "
        "grpo_extra_config, model_config, reward_config, and optional lora_config."
    ),
    "ModelTrainOPDNode": (
        "Run OPD (On-Policy Distillation) training with student/teacher model configs and return output directory."
    ),
    "DatasetValidatorNode": "Validates dataset configuration and generates preview HTML plus metrics YAML.",
}

PARAM_DESC_EN: dict[str, str] = {
    "train_data_path": "Training data path",
    "val_data_path": "Validation data path",
    "dataset_kind_config": "Kind config YAML from Vision/Text/Messages builder",
    "dataset_extra_config": "Extra config YAML from Dataset Extra Config Builder",
    "dataset_config": "Dataset configuration YAML string",
    "training_config": "Training configuration YAML string",
    "model_config": "Model configuration YAML string",
    "teacher_model_config": "Teacher model configuration YAML (OPD)",
    "lora_config": "LoRA configuration YAML string",
    "grpo_extra_config": "GRPO-only extra configuration YAML",
    "reward_config": "Reward configuration YAML string",
    "wandb_config": "W&B configuration",
    "model_output_path": "Trained model output directory",
    "output_path": "Output directory path",
    "thinking_as_input_ratio": "Include chain-of-thought content as input at the given ratio",
    "image_field": "Image field name in dataset records",
    "system_prompt_field": "System prompt field name",
    "user_prompt_field": "User prompt field name",
    "assistant_response_field": "Assistant response field name",
    "rejected_field": "Rejected response field name (DPO)",
    "messages_field": "Messages field name",
    "model_path": "Base model path or HuggingFace model ID",
    "lora_path": "LoRA adapter directory path",
    "merged_model_path": "Merged model output path",
    "wandb_api_key": "W&B API key",
    "wandb_project": "W&B project name",
    "wandb_name": "W&B run name",
    "lmbda": "OPD lambda hyperparameter",
    "beta": "OPD beta hyperparameter",
    "temperature": "Sampling temperature",
    "max_new_tokens": "Maximum new tokens to generate",
    "seq_kd": "Enable sequence-level knowledge distillation",
}

OUTPUT_DESC_EN: dict[str, str] = {
    "dataset_config": "Built dataset configuration YAML string",
    "dataset_kind_config": "Built dataloader kind configuration YAML string",
    "dataset_extra_config": "Built dataset extra configuration YAML string",
    "training_config": "Built training configuration YAML string",
    "model_config": "Built model configuration YAML string",
    "lora_config": "Built LoRA configuration YAML string",
    "reward_config": "Built reward configuration YAML string",
    "reward_item": "Built reward item YAML string",
    "metrics_config": "Built metrics configuration YAML string",
    "grpo_extra_config": "Built GRPO extra configuration YAML string",
    "accelerate_config": "Accelerate configuration YAML",
    "wandb_config": "W&B configuration YAML",
    "model_output_path": "Trained model output directory path",
    "merged_model_path": "Merged model output directory path",
    "augmentation_path": "Augmented dataset output path",
    "benchmark_output_path": "Benchmark report output path",
    "metrics_yaml": "Validation metrics YAML string",
    "output_preview_path": "Generated preview HTML file path",
    "jsonl_path": "Output JSONL file path",
}

OVERVIEW_ZH: dict[str, str] = {
    "DatasetConfigBuilderNode": "构建用于 SFT/GRPO/DPO 训练的数据集配置 YAML 字符串。组合数据路径、dataset_kind_config 与 dataset_extra_config。",
    "DatasetConfigBuilderVisionNode": "构建视觉（Vision）类型数据集的 kind 配置 YAML 字符串，供 Dataset Config Builder 使用。",
    "DatasetConfigBuilderTextNode": "构建纯文本类型数据集的 kind 配置 YAML 字符串，供 Dataset Config Builder 使用。",
    "DatasetConfigBuilderMessageNode": "构建 messages 格式数据集的 kind 配置 YAML 字符串，供 Dataset Config Builder 使用。",
    "DatasetExtraConfigBuilderNode": "构建数据集额外配置 YAML 字符串（collator 入口、max_seq_length、采样限制等）。",
    "DatasetValidatorNode": "校验数据集配置并生成数据预览 HTML 与指标 YAML。",
    "DatasetToJsonlNode": "将数据集转换为 JSONL 格式。",
    "LoraConfigBuilderNode": "构建 LoRA 配置 YAML 字符串。",
    "TrainingConfigBuilderNode": "构建 SFT/GRPO/DPO 共用的 training_config YAML 字符串（BaseTrainingConfig 字段）。",
    "ModelConfigBuilderNode": "构建模型配置 YAML 字符串。",
    "ModelTrainSFTNode": "运行 SFT 训练并返回模型输出目录。",
    "ModelTrainDPONode": "运行 DPO 训练并返回模型输出目录。",
    "ModelTrainGRPONode": "GRPO 主训练节点，采用与 SFT 对齐的 YAML 配置，返回训练好的模型目录。",
    "ModelTrainOPDNode": "运行 OPD（On-Policy Distillation）训练并返回模型输出目录。",
    "ModelEvalApiNode": "通过 Inference API 离线评估模型：加载 benchmark 数据集、批量调用部署端点、计算任务级指标并输出报告。",
    "MetricsConfigBuilderNode": "构建系统内置 metrics 配置 YAML。",
    "MetricsConfigBuilderCustomNode": "构建自定义 entry 的 metrics 配置 YAML。",
    "RewardItemBuilderNode": "构建单个 reward item YAML（系统内置 entry）。非空 kwargs 表示 factory=true。",
    "RewardItemBuilderCustomNode": "构建单个 reward item YAML（自定义 entry）。非空 kwargs 表示 factory=true。",
    "DataPreprocessPromptExpandNode": "运行 data_preprocess prompt-expand 流水线并输出增强后的数据路径。",
}


def load_node_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def fmt_default(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str) and value == "":
        return "''"
    return str(value)


def param_description_en(param: dict) -> str:
    parts: list[str] = []
    name = param["name"]
    if name in PARAM_DESC_EN:
        parts.append(PARAM_DESC_EN[name])
    desc_extra = param.get("description")
    if desc_extra:
        parts.append(str(desc_extra))
    if "default" in param:
        parts.append(f"Default: `{fmt_default(param['default'])}`")
    enum_vals = (param.get("config") or {}).get("enum")
    if enum_vals:
        parts.append(f"Options: {', '.join(enum_vals)}")
    return ". ".join(parts) if parts else "-"


def param_description_zh(param: dict) -> str:
    name = param["name"]
    zh_map = {
        "train_data_path": "训练数据路径",
        "val_data_path": "验证数据路径",
        "dataset_kind_config": "数据集 kind 配置 YAML 字符串（来自 Vision/Text/Messages Builder）",
        "dataset_extra_config": "数据集额外配置 YAML 字符串（来自 Dataset Extra Config Builder）",
        "dataset_config": "数据集配置 YAML 字符串",
        "training_config": "训练配置 YAML 字符串",
        "model_config": "模型配置 YAML 字符串",
        "teacher_model_config": "教师模型配置 YAML 字符串（OPD 用）",
        "lora_config": "LoRA 配置 YAML 字符串",
        "grpo_extra_config": "GRPO 专属配置 YAML 字符串",
        "reward_config": "奖励配置 YAML 字符串",
        "wandb_config": "W&B 配置",
        "model_output_path": "模型输出目录路径",
        "output_path": "输出目录路径",
        "thinking_as_input_ratio": "将思维链内容按比例作为输入的一部分。",
        "image_field": "图片字段名",
        "system_prompt_field": "系统提示字段名",
        "user_prompt_field": "用户提示字段名",
        "assistant_response_field": "助手回复字段名",
        "rejected_field": "拒绝回复字段名（DPO 用）",
        "messages_field": "messages 字段名",
        "model_path": "模型路径或 HuggingFace 模型 ID",
        "lora_path": "LoRA adapter 目录路径",
        "merged_model_path": "合并后模型输出路径",
        "augmentation_path": "数据增强输出路径",
        "benchmark_output_path": "Benchmark 报告输出路径",
        "metrics_yaml": "校验指标 YAML 字符串",
        "output_preview_path": "数据预览 HTML 文件路径",
        "jsonl_path": "输出 JSONL 文件路径",
        "dataset_path": "输入数据集路径",
        "endpoint": "Inference API 端点 URL",
        "endpoint_api_key": "Inference API 密钥",
        "endpoint_model": "Inference API 模型名称",
        "metrics_config": "评估指标配置 YAML 字符串",
        "lmbda": "OPD lmbda 超参数",
        "beta": "OPD beta 超参数",
        "temperature": "采样温度",
        "max_new_tokens": "最大生成 token 数",
        "seq_kd": "是否启用 sequence-level KD",
    }
    parts: list[str] = []
    if name in zh_map:
        parts.append(zh_map[name])
    if "default" in param:
        parts.append(f"默认值：`{fmt_default(param['default'])}`")
    enum_vals = (param.get("config") or {}).get("enum")
    if enum_vals:
        parts.append(f"可选值：{', '.join(enum_vals)}")
    text = "。".join(parts) if parts else param_description_en(param)
    return text.replace("。。", "。")


def build_param_rows(params: list[dict], lang: str) -> str:
    if lang == "zh":
        header = "| 参数 | 数据类型 | 必填 | 描述 |\n|------|---------|------|------|\n"
        req_map = {"required": "是", "optional": "否"}
        desc_fn = param_description_zh
    else:
        header = "| Parameter | Data Type | Required | Description |\n|-----------|-----------|----------|-------------|\n"
        req_map = {"required": "Yes", "optional": "No"}
        desc_fn = param_description_en

    rows = []
    for p in params:
        if p.get("type") != "input":
            continue
        rows.append(
            f"| {p['name']} | {p['dtype']} | {req_map.get(p.get('required_type', 'optional'), 'No')} | {desc_fn(p)} |"
        )
    return header + "\n".join(rows) + "\n"


def build_output_rows(params: list[dict], lang: str) -> str:
    if lang == "zh":
        header = "| 参数 | 数据类型 | 描述 |\n|------|---------|------|\n"
    else:
        header = "| Parameter | Data Type | Description |\n|-----------|-----------|-------------|\n"

    rows = []
    for p in params:
        if p.get("type") != "output":
            continue
        if lang == "zh":
            desc = {
                "dataset_config": "构建的数据集配置 YAML 字符串",
                "dataset_kind_config": "构建的 kind 配置 YAML 字符串",
                "dataset_extra_config": "构建的额外配置 YAML 字符串",
                "training_config": "构建的训练配置 YAML 字符串",
                "model_config": "构建的模型配置 YAML 字符串",
                "lora_config": "构建的 LoRA 配置 YAML 字符串",
                "reward_config": "构建的 reward 配置 YAML 字符串",
                "reward_item": "构建的 reward item YAML 字符串",
                "metrics_config": "构建的 metrics 配置 YAML 字符串",
                "grpo_extra_config": "构建的 GRPO 额外配置 YAML 字符串",
                "accelerate_config": "Accelerate 配置 YAML",
                "wandb_config": "W&B 配置 YAML",
                "model_output_path": "模型输出目录路径",
                "merged_model_path": "合并后模型输出路径",
                "augmentation_path": "数据增强输出路径",
                "benchmark_output_path": "Benchmark 报告输出路径",
                "metrics_yaml": "校验指标 YAML 字符串",
                "output_preview_path": "数据预览 HTML 文件路径",
                "jsonl_path": "输出 JSONL 文件路径",
            }.get(p["name"], p["name"])
        else:
            desc = OUTPUT_DESC_EN.get(p["name"], p["name"])
        rows.append(f"| {p['name']} | {p['dtype']} | {desc} |")
    return header + "\n".join(rows) + "\n"


def camel_task_name(node_name: str) -> str:
    if node_name[0].isupper():
        return node_name[0].lower() + node_name[1:]
    return node_name


def render_doc(node: dict, lang: str) -> str:
    name = node["name"]
    display = node.get("display_name") or DISPLAY_NAME_EN.get(name, name)
    overview = node.get("description", "").strip()
    if lang == "zh":
        overview = OVERVIEW_ZH.get(name, overview)
        title = f"# {display} 节点"
        sec_overview = "## 1.1 功能概述"
        sec_input = "## 1.2 输入类型"
        sec_output = "## 1.3 输出类型"
        sec_workflow = "## 1.4 Workflow JSON 定义"
        sec_run = "## 1.5 运行 Workflow"
        workflow_text = f"完整 workflow 定义见 [`workflow/{name}/{name}.json`](../../workflow/{name}/{name}.json)。"
        opt_name = "任务名称"
        opt_output = "输出结果文件"
        opt_poll = "轮询间隔（秒）"
        opt_timeout = "最大等待时间（秒）"
        opt_pretty = "美化 JSON 输出"
        opt_retries = "API 请求最大重试次数"
        opt_help = "显示帮助信息"
    else:
        overview = OVERVIEW_EN.get(name, overview)
        title = f"# {display} Node"
        sec_overview = "## 1.1 Overview"
        sec_input = "## 1.2 Input"
        sec_output = "## 1.3 Output"
        sec_workflow = "## 1.4 Workflow JSON Definition"
        sec_run = "## 1.5 Running the Workflow"
        workflow_text = (
            f"See [`workflow/{name}/{name}.json`](../../workflow/{name}/{name}.json) "
            f"for the full workflow definition."
        )
        opt_name = "Task name"
        opt_output = "Output results file"
        opt_poll = "Poll interval in seconds"
        opt_timeout = "Max wait time in seconds"
        opt_pretty = "Pretty-print JSON output"
        opt_retries = "Max retries for API requests"
        opt_help = "Show help message"

    img_path = f"/imgs/{name}/{name}.png"
    params = node.get("parameters") or []
    task_name = camel_task_name(name)

    body = f"""{title}

![alt text]({img_path})

{sec_overview}

{overview}

{sec_input}

{build_param_rows(params, lang)}
{sec_output}

{build_output_rows(params, lang)}
{sec_workflow}

{workflow_text}

{sec_run}

```bash
export PYROMIND_API_KEY=<your-api-key>
python -m pyromind_sdk.test_run_workflow_cli workflow/{name}/{name}.json [options]
```

| {"选项" if lang == "zh" else "Option"} | {"默认值" if lang == "zh" else "Default"} | {"说明" if lang == "zh" else "Description"} |
|{"------|--------|------" if lang == "zh" else "--------|---------|-------------"}|
| `--name` | `{task_name}` | {opt_name} |
| `--output` | - | {opt_output} |
| `--poll-interval` | 5 | {opt_poll} |
| `--timeout` | 600 | {opt_timeout} |
| `--pretty` | false | {opt_pretty} |
| `--max-retries` | 0 | {opt_retries} |
| `-h, --help` | - | {opt_help} |
"""
    return body


def merge_preserve_sections(existing: str, generated: str) -> str:
    """Keep custom example/json blocks from existing docs when regenerating."""
    for section_key in ("## 1.4", "## 1.5"):
        pattern = rf"({re.escape(section_key)}.*?)(?=\n## |\Z)"
        old_match = re.search(pattern, existing, re.DOTALL)
        if not old_match:
            continue
        old_block = old_match.group(1)
        if "```json" in old_block or "Example" in old_block or "示例" in old_block or "输出示例" in old_block:
            gen_match = re.search(pattern, generated, re.DOTALL)
            if gen_match:
                generated = generated[: gen_match.start()] + old_block + generated[gen_match.end() :]
    return generated


def write_doc(node: dict, lang: str, out_root: Path) -> None:
    name = node["name"]
    out_dir = out_root / name
    out_file = out_dir / f"{name}.md"
    generated = render_doc(node, lang)
    if out_file.exists():
        existing = out_file.read_text(encoding="utf-8")
        generated = merge_preserve_sections(existing, generated)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file.write_text(generated, encoding="utf-8")
    print(f"Wrote {out_file}")


def main() -> None:
    yaml_files = sorted(NODES_DIR.glob("*.yaml"))
    for path in yaml_files:
        node = load_node_yaml(path)
        if not node or "name" not in node:
            continue
        write_doc(node, "en", DOCS_EN)
        write_doc(node, "zh", DOCS_ZH)


if __name__ == "__main__":
    main()
