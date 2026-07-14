#!/usr/bin/env python3
"""Synchronize documented node I/O types with the PyroMind API."""

from __future__ import annotations

import re
from pathlib import Path

from pyromind_sdk import PyroMindAPIClient


ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOTS = (ROOT / "docs", ROOT / "docs_zh")


def normalize_type(raw_type: object) -> str:
    """Return the type token exposed by the SDK, including union types."""
    if isinstance(raw_type, list):
        return normalize_type(raw_type[0]) if raw_type else "STRING"
    return str(raw_type).upper()


def node_types(info: dict) -> tuple[dict[str, str], dict[str, str]]:
    inputs: dict[str, str] = {}
    for group in ("required", "optional"):
        for name, spec in info.get("input", {}).get(group, {}).items():
            inputs[name] = normalize_type(spec)

    outputs = {
        name: normalize_type(types[index]) if index < len(types) else ""
        for index, name in enumerate(info.get("output_name", []))
        for types in (info.get("output", []),)
    }
    return inputs, outputs


def update_table(section: str, types: dict[str, str], column_count: int) -> tuple[str, int]:
    lines = section.splitlines()
    has_trailing_newline = section.endswith("\n")
    updated = 0
    for index, line in enumerate(lines):
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.split("|")]
        values = cells[1:-1]
        if len(values) < column_count:
            continue
        name = values[0]
        dtype = types.get(name)
        display_type = dtype.replace("|", "\\|") if dtype else ""
        if dtype:
            if len(values) == column_count:
                remainder = values[2:]
            else:
                # Repair rows written before union-type pipes were escaped.
                type_cells = len(dtype.split("|"))
                if values[1].endswith("\\"):
                    # A partially escaped value was split once, then its final
                    # union token was duplicated by an earlier synchronizer.
                    type_cells += 1
                remainder = values[1 + type_cells :]
            normalized = [name, display_type, *remainder]
            new_line = "| " + " | ".join(normalized) + " |"
            if new_line != line:
                lines[index] = new_line
                updated += 1
    result = "\n".join(lines)
    return (result + "\n" if has_trailing_newline else result), updated


def update_document(path: Path, inputs: dict[str, str], outputs: dict[str, str]) -> int:
    text = path.read_text()
    count = 0
    patterns = (
        (r"(##\s+.*(?:Input|输入类型)\s*\n)(.*?)(?=\n##\s|\Z)", inputs, 4),
        (r"(##\s+.*(?:Output|输出类型)\s*\n)(.*?)(?=\n##\s|\Z)", outputs, 3),
    )
    for pattern, types, column_count in patterns:
        def replace(match: re.Match[str]) -> str:
            nonlocal count
            table, changed = update_table(match.group(2), types, column_count)
            count += changed
            return match.group(1) + table

        text = re.sub(pattern, replace, text, flags=re.DOTALL)
    if count:
        path.write_text(text)
    return count


def main() -> None:
    nodes = PyroMindAPIClient().studio.get_node_info()
    changed_files = 0
    changed_types = 0
    for node_name, info in nodes.items():
        inputs, outputs = node_types(info)
        for docs_root in DOCS_ROOTS:
            path = docs_root / node_name / f"{node_name}.md"
            if not path.exists():
                continue
            changed = update_document(path, inputs, outputs)
            if changed:
                changed_files += 1
                changed_types += changed
                print(f"Updated {path.relative_to(ROOT)} ({changed} type fields)")
    print(f"Synchronized {changed_types} type fields in {changed_files} documents.")


if __name__ == "__main__":
    main()
