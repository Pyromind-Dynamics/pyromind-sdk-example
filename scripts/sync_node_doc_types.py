#!/usr/bin/env python3
"""Synchronize documented node I/O tables with the PyroMind API definitions.

For every node document this script:

- updates the Data Type cell of existing input/output rows,
- updates the Required cell of input rows to match the definition,
- appends rows that exist in the definition but are missing from the table
  (with a description taken from the doc generator's curated maps).

By default definitions are fetched live through ``PyroMindAPIClient`` for the
cluster in ``--cluster`` (default ``us-west-2#pre``). Pass ``--defs <json>`` to
sync against a saved ``studio.get_node_info()`` snapshot instead, and
``--check`` to report mismatches without writing anything.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from pyromind_sdk import PyroMindAPIClient

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS_ROOTS = (ROOT / "docs", ROOT / "docs_zh")
DEFAULT_CLUSTER = "us-west-2#pre"
DEFAULT_BASE_URL = "https://pre-api-portal.pyromind.ai/api/v1/"
DEFAULT_REPO = ROOT

# Reuse curated per-parameter descriptions from the doc generator when it lives
# next to this script; fall back to compact built-ins otherwise.
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from generate_node_docs import PARAM_DESC_EN, PARAM_DESC_ZH  # type: ignore
except Exception:  # pragma: no cover - standalone skill copy without the generator
    PARAM_DESC_EN = {}
    PARAM_DESC_ZH = {}

FALLBACK_DESC_EN = {
    "gpu_count": "Number of GPUs requested",
    "gpu_product": "GPU product name (follow the GPUs actually available in the target environment)",
    "accelerate_config": "Accelerate launch configuration YAML",
    "dataset_config": "Assembled dataset configuration YAML string",
    "dataset": "Dataset identifier or path",
    "dataset_name": "Dataset identifier or path",
    "dataset_path": "Input dataset directory path",
    "dataset_kind_config": "Dataset kind config YAML from a Kind Config Builder node",
    "dataset_extra_config": "Dataset extra config YAML from Dataset Extra Config Builder",
    "ground_truths": "Ground-truth answers used to validate completions",
    "endpoint_api_key": "Inference API key",
    "endpoint_model": "Model name served by the inference endpoint",
    "model_path": "Model path",
    "wandb_config": "W&B configuration object",
    "image_field": "Image field name",
    "completions": "Completions JSON for reward validation",
    "dataset_config": "Dataset configuration YAML string",
}

FALLBACK_DESC_ZH = {
    "gpu_count": "GPU 数量",
    "gpu_product": "GPU 型号（以部署环境实际可用的显卡为准）",
    "accelerate_config": "Accelerate 启动配置 YAML",
    "dataset_config": "已组装的数据集配置 YAML 字符串",
    "dataset": "数据集名称或路径",
    "dataset_name": "数据集名称或路径",
    "dataset_path": "输入数据集目录路径",
    "dataset_kind_config": "来自 Kind Config Builder 节点的 dataset kind 配置 YAML",
    "dataset_extra_config": "来自 Dataset Extra Config Builder 节点的额外配置 YAML",
    "ground_truths": "用于校验 completions 的 ground-truth 数据",
    "endpoint_api_key": "推理 API Key",
    "endpoint_model": "推理端点提供的模型名称",
    "model_path": "模型路径",
    "wandb_config": "W&B 配置对象",
    "image_field": "图片字段名",
    "completions": "用于奖励校验的 completions JSON",
}


def normalize_type(raw_type: object) -> str:
    """Return the type token exposed by the SDK, including union types."""
    if isinstance(raw_type, list):
        return normalize_type(raw_type[0]) if raw_type else "STRING"
    return str(raw_type).upper()


def node_io(info: dict) -> tuple[dict[str, tuple], dict[str, tuple], list[str], list[str]]:
    """Return input/output row specs and their definition order.

    ``{name: (type, required_or_None)}`` plus the raw definition spec used to
    render a description for appended rows.
    """
    inputs: dict[str, tuple] = {}
    input_order: list[str] = []
    for group in ("required", "optional"):
        for name, spec in info.get("input", {}).get(group, {}).items():
            inputs[name] = (normalize_type(spec), group == "required", spec)
            input_order.append(name)

    outputs: dict[str, tuple] = {}
    output_order: list[str] = []
    for index, name in enumerate(info.get("output_name", [])):
        types = info.get("output", [])
        raw = types[index] if index < len(types) else ""
        outputs[name] = (normalize_type(raw), None, raw)
        output_order.append(name)
    return inputs, outputs, input_order, output_order


def _config(spec: object) -> dict:
    if isinstance(spec, list) and len(spec) > 1 and isinstance(spec[1], dict):
        return spec[1]
    if isinstance(spec, dict):
        return spec.get("config") or spec
    return {}


def _fmt_default(value, lang: str) -> str:
    if value is None:
        return "-"
    if value == "":
        return "空字符串" if lang == "zh" else "empty string"
    if isinstance(value, bool):
        return "true" if value else "false"
    return f"`{value}`"


def _param_desc(name: str, spec: object, lang: str) -> str:
    desc_map = PARAM_DESC_ZH if lang == "zh" else PARAM_DESC_EN
    fallback = FALLBACK_DESC_ZH if lang == "zh" else FALLBACK_DESC_EN
    base = desc_map.get(name) or fallback.get(name) or name.replace("_", " ").capitalize()
    config = _config(spec)
    enum_vals = config.get("enum")
    if isinstance(enum_vals, list) and enum_vals:
        if lang == "zh":
            return f"{base}。选项：{'、'.join(f'`{v}`' for v in enum_vals)}"
        return f"{base}. Options: {', '.join(f'`{v}`' for v in enum_vals)}"
    default = config.get("default")
    if default is not None:
        d = _fmt_default(default, lang)
        return f"{base}。默认值：{d}" if lang == "zh" else f"{base}. Default: {d}"
    return base


def _read_cells(line: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def _req_text(required: bool, lang: str) -> str:
    return ("是" if required else "否") if lang == "zh" else ("Yes" if required else "No")


def _reflow_row(
    cells: list[str], dtype: str, required: bool | None, lang: str, column_count: int
) -> str:
    """Rebuild one table row: name | type | [required] | description."""
    display_type = dtype.replace("|", "\\|")
    # Extra cells beyond the fixed columns belong to a union type that was
    # written with escaped pipes; re-join them so the description survives.
    type_n = max(len(cells) - column_count + 1, 1)
    rest = cells[1 + type_n :]
    if required is None:  # output table: name | type | description
        desc = "|".join(rest)
        return f"| {cells[0]} | {display_type} | {desc} |"
    desc = "|".join(rest[1:]) if rest else ""
    return f"| {cells[0]} | {display_type} | {_req_text(required, lang)} | {desc} |"


def update_table(
    section: str,
    rows: dict[str, tuple],
    order: list[str],
    column_count: int,
    lang: str,
) -> tuple[str, int, list[str]]:
    """Rewrite one table; return (text, changed_rows, appended_params)."""
    lines = section.splitlines()
    has_trailing_newline = section.endswith("\n")
    updated = 0
    last_table_row = -1
    present: set[str] = set()

    for index, line in enumerate(lines):
        if not line.startswith("|") or "---" in line:
            continue
        cells = _read_cells(line)
        if len(cells) < 2 or cells[0] in {"Parameter", "参数"}:
            continue
        spec = rows.get(cells[0])
        if spec is None:
            continue
        last_table_row = index
        present.add(cells[0])
        dtype, required, _raw = spec
        new_line = _reflow_row(cells, dtype, required, lang, column_count)
        if new_line != line:
            lines[index] = new_line
            updated += 1

    missing = [name for name in order if name not in present]
    if missing:
        insert_at = last_table_row + 1 if last_table_row >= 0 else 1
        added: list[str] = []
        for name in missing:
            dtype, required, raw = rows[name]
            display_type = dtype.replace("|", "\\|")
            if required is None:
                added.append(
                    f"| {name} | {display_type} | {_param_desc(name, raw, lang)} |"
                )
            else:
                added.append(
                    f"| {name} | {display_type} | {_req_text(required, lang)} | "
                    f"{_param_desc(name, raw, lang)} |"
                )
        lines[insert_at:insert_at] = added
        last_table_row += len(added)

    result = "\n".join(lines)
    return (result + "\n" if has_trailing_newline else result), updated, missing


def update_document(
    path: Path,
    inputs: dict[str, tuple],
    outputs: dict[str, tuple],
    input_order: list[str],
    output_order: list[str],
    lang: str,
) -> tuple[int, list[str]]:
    text = path.read_text()
    count = 0
    appended: list[str] = []
    patterns = (
        (r"(##\s+.*(?:Input|输入类型)\s*\n)(.*?)(?=\n##\s|\Z)", inputs, input_order, 4),
        (r"(##\s+.*(?:Output|输出类型)\s*\n)(.*?)(?=\n##\s|\Z)", outputs, output_order, 3),
    )

    def replace(pattern: str, rows: dict[str, tuple], order: list[str], column_count: int) -> str:
        nonlocal count, appended

        def repl(match: re.Match[str]) -> str:
            nonlocal count
            table, changed, miss = update_table(match.group(2), rows, order, column_count, lang)
            count += changed
            appended.extend(miss)
            return match.group(1) + table

        return re.sub(pattern, repl, text, flags=re.DOTALL)

    text = replace(*patterns[0])
    text = replace(*patterns[1])
    if count or appended:
        path.write_text(text)
    return count, appended


def check_document(
    path: Path,
    inputs: dict[str, tuple],
    input_order: list[str],
    lang: str,
) -> list[str]:
    """Return issue descriptions; does not modify the file."""
    issues: list[str] = []
    text = path.read_text()
    match = re.search(r"##\s+.*(?:Input|输入类型)\s*\n(.*?)(?=\n##\s|\Z)", text, re.DOTALL)
    if not match:
        return [f"{path.name}: missing input section"]
    present: set[str] = set()
    for line in match.group(1).splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = _read_cells(line)
        if len(cells) < 3 or cells[0] in {"Parameter", "参数"}:
            continue
        spec = inputs.get(cells[0])
        if spec is None:
            continue
        present.add(cells[0])
        dtype, required, _raw = spec
        if cells[1].replace("\\|", "|") != dtype:
            issues.append(f"{cells[0]}: type {cells[1]!r} != def {dtype!r}")
        req_cell = cells[2] if len(cells) >= 3 else ""
        want = _req_text(required, lang)
        if req_cell != want:
            issues.append(f"{cells[0]}: required {req_cell!r} != def {want!r}")
    for name in input_order:
        if name not in present:
            issues.append(f"{name}: missing row in doc table")
    return issues


def load_defs(defs_path: str | None, cluster: str) -> dict:
    if defs_path:
        with open(defs_path, encoding="utf-8") as f:
            return json.load(f)
    return PyroMindAPIClient(
        api_key=os.environ.get("PYROMIND_API_KEY"),
        base_url=os.environ.get("PYROMIND_BASE_URL") or DEFAULT_BASE_URL,
        cluster=cluster,
    ).studio.get_node_info()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--defs", help="path to a saved get_node_info() JSON snapshot")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="repository root containing docs/ and docs_zh/ (default: %(default)s)")
    parser.add_argument("--cluster", default=DEFAULT_CLUSTER, help="cluster to fetch definitions from (default: %(default)s)")
    parser.add_argument("--check", action="store_true", help="report mismatches without writing")
    args = parser.parse_args()
    if Path(args.repo).resolve() != ROOT and not Path(args.repo).exists():
        parser.error(f"--repo does not exist: {args.repo}")
    docs_roots = (Path(args.repo) / "docs", Path(args.repo) / "docs_zh")

    defs = load_defs(args.defs, args.cluster)
    total_changed = 0
    total_appended: list[str] = []
    total_issues: list[str] = []

    for node_name, info in defs.items():
        inputs, outputs, input_order, output_order = node_io(info)
        if not inputs and not outputs:
            continue
        for docs_root in docs_roots:
            path = docs_root / node_name / f"{node_name}.md"
            if not path.exists():
                continue
            lang = "zh" if docs_root.name == "docs_zh" else "en"
            if args.check:
                issues = check_document(path, inputs, input_order, lang)
                if issues:
                    total_issues.append(f"{path.relative_to(ROOT)}:")
                    total_issues.extend(f"  - {msg}" for msg in issues)
                continue
            changed, appended = update_document(path, inputs, outputs, input_order, output_order, lang)
            if changed or appended:
                total_changed += changed
                total_appended.extend(appended)
                print(f"Updated {path.relative_to(ROOT)} ({changed} type/required cells, +{len(appended)} rows {appended or ''})")

    if args.check:
        print(f"Checked {len(defs)} node definitions; issues={len(total_issues)}")
        if total_issues:
            print("\n".join(total_issues))
        return
    print(f"Synchronized {total_changed} cells and appended {len(total_appended)} rows.")


if __name__ == "__main__":
    main()
