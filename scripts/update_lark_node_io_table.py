#!/usr/bin/env python3
"""Update the Lark node I/O sheet from system and user node definitions.

Sources:
- system nodes: local k8s_middleware Python classes
- custom/share nodes: YAML files under a user's storage /workspace/nodes

The script only writes the existing sheet's input/output columns.
"""

from __future__ import annotations

import argparse
import ast
import csv
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

DEFAULT_LARK_URL = "https://dcn8r6br8g3u.feishu.cn/wiki/NZBnwHZosihP2wkbpdqcBhEhnld?sheet=WRoVgw"
DEFAULT_SHEET_ID = "WRoVgw"
DEFAULT_K8S_PATH = Path("/Users/wyl/Desktop/project/code/background/k8s_middleware")
DEFAULT_STORAGE_BUCKET = "1000003786"
DEFAULT_STORAGE_PREFIX = "nodes"

STRUCTURED_NAME_RE = re.compile(
    r"(^|_)(config|yaml|json|schema|item|payload|params?|kwargs?)($|_)", re.I
)
CONFIG_NAME_RE = re.compile(r"(^|_)config($|_)", re.I)


@dataclass
class Param:
    name: str
    dtype: str
    required: bool = False
    default: Any = None
    enum: list[Any] = field(default_factory=list)
    description: str = ""
    fields: list["Param"] = field(default_factory=list)


@dataclass
class NodeSpec:
    name: str
    node_type: str = ""
    inputs: list[Param] = field(default_factory=list)
    outputs: list[Param] = field(default_factory=list)
    description: str = ""
    source: str = ""


def _run_json(cmd: list[str], stdin: str | None = None) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )
    text = proc.stdout.strip() or proc.stderr.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Command returned non-JSON output: {' '.join(cmd)}\n{text}") from exc
    if proc.returncode != 0 or (not data.get("ok", False) and "api" not in data):
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{json.dumps(data, ensure_ascii=False, indent=2)}")
    return data


def _dtype(raw: Any) -> str:
    if isinstance(raw, (tuple, list)):
        if not raw:
            return "STRING"
        return "|".join(str(item).upper() for item in raw)
    if raw is None:
        return "STRING"
    return str(raw).upper()


def _dtype_parts(dtype: str) -> set[str]:
    return {part.strip().upper() for part in re.split(r"[|｜,]", dtype) if part.strip()}


def _is_string_dtype(dtype: str) -> bool:
    return "STRING" in _dtype_parts(dtype)


def _config(raw: Any) -> dict[str, Any]:
    if isinstance(raw, (tuple, list)) and len(raw) > 1 and isinstance(raw[1], dict):
        return raw[1]
    if isinstance(raw, dict):
        return raw.get("config") or raw
    return {}


def _clean(text: Any) -> str:
    if not text:
        return ""
    return " ".join(str(text).split())


def _safe_literal(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def _extract_class_attr(class_node: ast.ClassDef, attr_name: str) -> Any:
    for stmt in class_node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == attr_name:
                    return _safe_literal(stmt.value)
    return None


def _extract_input_types(class_node: ast.ClassDef) -> dict[str, Any]:
    for stmt in class_node.body:
        if not isinstance(stmt, ast.FunctionDef) or stmt.name not in {"INPUT_TYPES", "BASE_INPUT_TYPES"}:
            continue
        for inner in ast.walk(stmt):
            if isinstance(inner, ast.Return):
                value = _safe_literal(inner.value)
                if isinstance(value, dict):
                    return value
    return {"required": {}, "optional": {}}


def _resource_inputs(class_node: ast.ClassDef, bases: set[str]) -> dict[str, Any]:
    required: dict[str, Any] = {}
    if "PortPodExecutionNode" in bases:
        required["port"] = ("INT", {"default": 3000, "min": 1, "max": 8000})
    if "GpuPodExecutionNode" in bases:
        required["gpu_count"] = ("INT", {"default": 1, "min": 1, "max": 8})
        required["gpu_product"] = (
            "STRING",
            {"default": "NVIDIA-H100-NVL", "enum": ["NVIDIA-H100-NVL", "NVIDIA-L40S"]},
        )
    return required


def _base_names(class_node: ast.ClassDef) -> set[str]:
    names = set()
    for base in class_node.bases:
        if isinstance(base, ast.Name):
            names.add(base.id)
        elif isinstance(base, ast.Attribute):
            names.add(base.attr)
    return names


def _params_from_mapping(mapping: dict[str, Any], required: bool) -> list[Param]:
    params = []
    for name, spec in mapping.items():
        cfg = _config(spec)
        raw_enum = cfg.get("enum")
        enum = list(raw_enum) if isinstance(raw_enum, (list, tuple)) else []
        params.append(
            Param(
                name=str(name),
                dtype=_dtype(spec),
                required=required,
                default=cfg.get("default"),
                enum=enum,
                description=_clean(cfg.get("description") or cfg.get("desc")),
            )
        )
    return params


def load_system_specs(k8s_path: Path) -> dict[str, NodeSpec]:
    builtin_dir = k8s_path / "app/models/nodes/builtin_nodes"
    specs: dict[str, NodeSpec] = {}
    for py_path in sorted(builtin_dir.glob("*.py")):
        tree = ast.parse(py_path.read_text())
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            bases = _base_names(node)
            if not bases & {
                "BaseNode",
                "PodExecutionNode",
                "EndpointNode",
                "GpuPodExecutionNode",
                "PortPodExecutionNode",
                "DaemonPodExecutionNode",
                "TemplateAccessPodExecutionNode",
            }:
                continue
            if _extract_class_attr(node, "IS_INTERNAL") is True:
                continue
            input_types = _extract_input_types(node)
            req = dict(input_types.get("required") or {})
            opt = dict(input_types.get("optional") or {})
            req.update(_resource_inputs(node, bases))
            return_types = _extract_class_attr(node, "RETURN_TYPES") or ()
            return_names = _extract_class_attr(node, "RETURN_NAMES") or return_types
            outputs = [
                Param(name=str(return_names[i]), dtype=_dtype(t))
                for i, t in enumerate(return_types)
                if i < len(return_names)
            ]
            specs[node.name] = NodeSpec(
                name=node.name,
                node_type="system",
                inputs=[*_params_from_mapping(req, True), *_params_from_mapping(opt, False)],
                outputs=outputs,
                description=_clean(_extract_class_attr(node, "DESCRIPTION")),
                source=str(py_path),
            )
    return specs


def _storage_endpoint() -> tuple[str, bool]:
    endpoint = os.getenv("PYROMIND_STORAGE_ENDPOINT") or os.getenv("MINIO_ENDPOINT") or "https://storage.pyromind.ai"
    secure = True
    if endpoint.startswith(("http://", "https://")):
        parsed = urlparse(endpoint)
        secure = parsed.scheme == "https"
        endpoint = parsed.netloc
    return endpoint, secure


def _storage_credentials() -> tuple[str, str]:
    access_key = (
        os.getenv("PYROMIND_STORAGE_ACCESS_KEY")
        or os.getenv("MINIO_ACCESS_KEY")
        or os.getenv("AWS_ACCESS_KEY_ID")
    )
    secret_key = (
        os.getenv("PYROMIND_STORAGE_SECRET_KEY")
        or os.getenv("MINIO_SECRET_KEY")
        or os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    if not access_key or not secret_key:
        raise RuntimeError(
            "Missing storage credentials. Set PYROMIND_STORAGE_ACCESS_KEY/PYROMIND_STORAGE_SECRET_KEY "
            "or MINIO_ACCESS_KEY/MINIO_SECRET_KEY before reading custom nodes."
        )
    return access_key, secret_key


def _download_text(client: Any, bucket: str, object_name: str) -> str:
    response = client.get_object(bucket, object_name)
    try:
        return response.read().decode("utf-8")
    finally:
        response.close()
        response.release_conn()


def _workspace_to_key(path: str) -> str:
    path = path.strip()
    for prefix in ("/workspace/", "/target-workspace/"):
        if path.startswith(prefix):
            return path[len(prefix):]
    return path.lstrip("/")


def _candidate_code_keys(python_code: str, yaml_object_name: str) -> list[str]:
    primary = _workspace_to_key(python_code)
    candidates = [primary]
    if not python_code.startswith(("/", "s3://")):
        yaml_dir = str(Path(yaml_object_name).parent)
        candidates.append(f"{yaml_dir}/{python_code}".lstrip("./"))
    return list(dict.fromkeys(candidates))


def _const_str(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _name_of(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    return None


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_call_name(node.value)}.{node.attr}"
    return ""


def _dict_fields(node: ast.AST, prefix: str = "") -> list[Param]:
    """Infer object fields from a dict literal or a list of dict literals."""
    fields: list[Param] = []
    if isinstance(node, ast.Dict):
        for key, value in zip(node.keys, node.values):
            name = _const_str(key)
            if not name:
                continue
            field_name = f"{prefix}.{name}" if prefix else name
            fields.append(Param(name=field_name, dtype=_literal_dtype(value)))
            fields.extend(_dict_fields(value, field_name))
    elif isinstance(node, ast.List):
        for item in node.elts:
            item_fields = _dict_fields(item, prefix)
            if item_fields:
                fields.extend(item_fields)
                break
    return _dedupe_params(fields)


def _literal_dtype(node: ast.AST) -> str:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return "BOOLEAN"
        if isinstance(node.value, int):
            return "INT"
        if isinstance(node.value, float):
            return "FLOAT"
        if isinstance(node.value, str):
            return "STRING"
    if isinstance(node, ast.Dict):
        return "OBJECT"
    if isinstance(node, ast.List):
        return "LIST"
    return "*"


def _dedupe_params(params: list[Param]) -> list[Param]:
    seen: set[str] = set()
    result: list[Param] = []
    for param in params:
        if param.name in seen:
            continue
        seen.add(param.name)
        result.append(param)
    return result


def _slice_field(node: ast.AST) -> str | None:
    # Python 3.10 keeps slices directly; older AST used ast.Index.
    target = getattr(node, "value", node)
    return _const_str(target)


def _function_context_fields(code: str, function_name: str) -> dict[str, Any]:
    """Infer structured input/output fields from a custom node function body."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {}

    fn = next(
        (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == function_name),
        None,
    )
    if fn is None:
        return {}

    arg_names = {arg.arg for arg in fn.args.args}
    parsed_vars: dict[str, str] = {}
    loop_vars: dict[str, str] = {}
    dict_vars: dict[str, list[Param]] = {}
    input_fields: dict[str, list[Param]] = {name: [] for name in arg_names}
    output_fields: dict[str, list[Param]] = {}
    return_keys: list[str] = []

    def param_for_base(base: ast.AST | None) -> str | None:
        name = _name_of(base)
        if not name:
            return None
        if name in arg_names:
            return name
        if name in parsed_vars:
            return parsed_vars[name]
        if name in loop_vars:
            return loop_vars[name]
        return None

    for node in ast.walk(fn):
        if isinstance(node, ast.Assign):
            target_names = [_name_of(t) for t in node.targets]
            target_names = [t for t in target_names if t]
            if isinstance(node.value, ast.Call):
                call = _call_name(node.value.func)
                if call.endswith(("yaml.safe_load", "json.loads", "safe_load", "loads")) and node.value.args:
                    source = _name_of(node.value.args[0])
                    if source in arg_names:
                        for target in target_names:
                            parsed_vars[target] = source
            if isinstance(node.value, ast.Dict):
                for target in target_names:
                    dict_vars[target] = _dict_fields(node.value)

        elif isinstance(node, ast.For):
            iter_name = _name_of(node.iter)
            target_name = _name_of(node.target)
            source = parsed_vars.get(iter_name or "") or (iter_name if iter_name in arg_names else None)
            if target_name and source:
                loop_vars[target_name] = source

        elif isinstance(node, ast.Subscript):
            source = param_for_base(node.value)
            field = _slice_field(node.slice)
            if source and field:
                input_fields.setdefault(source, []).append(Param(name=field, dtype="*"))

        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            source = param_for_base(node.func.value)
            field = _const_str(node.args[0]) if node.args else None
            if source and field:
                input_fields.setdefault(source, []).append(Param(name=field, dtype="*"))

        elif isinstance(node, ast.Return):
            if isinstance(node.value, ast.Dict):
                for key, value in zip(node.value.keys, node.value.values):
                    output_name = _const_str(key)
                    if not output_name:
                        continue
                    return_keys.append(output_name)
                    fields = _dict_fields(value)
                    value_name = _name_of(value)
                    if not fields and value_name in dict_vars:
                        fields = dict_vars[value_name]
                    if fields:
                        output_fields[output_name] = fields
            else:
                value_name = _name_of(node.value)
                if value_name in dict_vars:
                    return_keys.extend([p.name for p in dict_vars[value_name]])

    return {
        "input_fields": {k: _dedupe_params(v) for k, v in input_fields.items() if v},
        "output_fields": {k: _dedupe_params(v) for k, v in output_fields.items() if v},
        "return_keys": list(dict.fromkeys(return_keys)),
    }


def _param_from_yaml(raw: dict[str, Any]) -> Param:
    cfg = raw.get("config") or {}
    return Param(
        name=str(raw["name"]),
        dtype=_dtype(raw.get("dtype") or raw.get("data_type")),
        required=raw.get("required_type") == "required" or raw.get("required") is True,
        default=raw.get("default", cfg.get("default")),
        enum=list(raw.get("enum") or cfg.get("enum") or []),
        description=_clean(raw.get("description") or raw.get("desc")),
    )


def load_storage_specs(bucket: str, prefix: str) -> dict[str, NodeSpec]:
    from minio import Minio
    from minio.error import S3Error

    endpoint, secure = _storage_endpoint()
    access_key, secret_key = _storage_credentials()
    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
    if hasattr(client, "_region_map"):
        client._region_map[bucket] = "us-east-1"
    prefix = prefix.strip("/")
    if prefix:
        prefix += "/"

    specs: dict[str, NodeSpec] = {}
    try:
        objects = list(client.list_objects(bucket, prefix=prefix, recursive=True))
    except S3Error as exc:
        raise RuntimeError(f"Failed to list storage bucket={bucket} prefix={prefix}: {exc}") from exc

    yaml_objects = [o.object_name for o in objects if o.object_name.endswith((".yaml", ".yml"))]
    code_cache: dict[str, str] = {}
    for object_name in yaml_objects:
        raw = yaml.safe_load(_download_text(client, bucket, object_name)) or {}
        if not isinstance(raw, dict) or not raw.get("name"):
            continue
        params = raw.get("parameters") or []
        inputs = [_param_from_yaml(p) for p in params if isinstance(p, dict) and p.get("type") == "input" and p.get("name")]
        outputs = [_param_from_yaml(p) for p in params if isinstance(p, dict) and p.get("type") == "output" and p.get("name")]

        code_fields: dict[str, Any] = {}
        python_code = raw.get("python_code") or raw.get("source_file_path")
        function_name = raw.get("function_name")
        if python_code and function_name:
            for code_key in _candidate_code_keys(str(python_code), object_name):
                try:
                    code = code_cache.get(code_key)
                    if code is None:
                        code = _download_text(client, bucket, code_key)
                        code_cache[code_key] = code
                    code_fields = _function_context_fields(code, str(function_name))
                    break
                except Exception:
                    code_fields = {}
        for param in inputs:
            inferred = (code_fields.get("input_fields") or {}).get(param.name)
            if inferred:
                param.fields = inferred
        for param in outputs:
            inferred = (code_fields.get("output_fields") or {}).get(param.name)
            if inferred:
                param.fields = inferred

        if code_fields.get("return_keys"):
            known = {p.name for p in outputs}
            for key in code_fields["return_keys"]:
                if key not in known:
                    outputs.append(
                        Param(
                            name=key,
                            dtype="*",
                            description="Returned by Python function",
                            fields=(code_fields.get("output_fields") or {}).get(key, []),
                        )
                    )

        specs[str(raw["name"])] = NodeSpec(
            name=str(raw["name"]),
            node_type=str(raw.get("node_type") or "user"),
            inputs=inputs,
            outputs=outputs,
            description=_clean(raw.get("description")),
            source=f"s3://{bucket}/{object_name}",
        )
    return specs


def build_payload_catalog(specs: dict[str, NodeSpec]) -> dict[str, list[Param]]:
    catalog: dict[str, list[Param]] = {}
    for spec in specs.values():
        for output in spec.outputs:
            if _is_string_dtype(output.dtype) and STRUCTURED_NAME_RE.search(output.name) and spec.inputs:
                catalog[output.name] = spec.inputs
    if "reward_item" in catalog:
        for i in range(1, 6):
            catalog[f"reward_item_{i}"] = catalog["reward_item"]
    if "model_config" in catalog:
        catalog["teacher_model_config"] = catalog["model_config"]
    return catalog


def _fmt_default(value: Any) -> str:
    if value is None:
        return ""
    if value == "":
        return "default: empty string"
    if isinstance(value, bool):
        return f"default: {'true' if value else 'false'}"
    return f"default: {value}"


def _display_dtype(param: Param, mark_config_objects: bool) -> str:
    if (
        mark_config_objects
        and param.dtype == "STRING"
        and CONFIG_NAME_RE.search(param.name)
    ):
        return "STRING|对象"
    return param.dtype


def _param_line(
    param: Param,
    catalog: dict[str, list[Param]],
    seen: set[str],
    mark_config_objects: bool,
    depth: int = 0,
) -> str:
    dtype = _display_dtype(param, mark_config_objects)
    bits = [f"{param.name}: {dtype}"]
    bits.append("required" if param.required else "optional")
    if param.enum:
        bits.append("options: " + ", ".join(map(str, param.enum)))
    default = _fmt_default(param.default)
    if default and not param.required:
        bits.append(default)
    if param.description:
        bits.append(param.description)
    line = "; ".join(bits)
    nested_fields = param.fields or catalog.get(param.name, [])
    if nested_fields and param.name not in seen and depth < 2:
        seen.add(param.name)
        child_lines = [
            _param_line(p, catalog, seen, mark_config_objects, depth + 1)
            for p in nested_fields
        ]
        label = "formatted fields" if _is_string_dtype(param.dtype) else "object fields"
        line += f"\n  {label}:\n" + "\n".join("    " + child for child in child_lines)
    return line


def render_params(
    params: list[Param],
    catalog: dict[str, list[Param]],
    empty_text: str,
    mark_config_objects: bool = False,
) -> str:
    if not params:
        return empty_text
    return "\n".join(
        _param_line(param, catalog, set(), mark_config_objects)
        for param in params
    )


def read_sheet_rows(url: str, sheet_id: str) -> list[dict[str, str]]:
    data = _run_json([
        "lark-cli", "sheets", "+csv-get",
        "--url", url,
        "--sheet-id", sheet_id,
        "--range", "A1:F200",
        "--max-chars", "120000",
    ])
    annotated = data["data"]["annotated_csv"]
    rows = []
    reader = csv.reader(io.StringIO(annotated))
    next(reader, None)
    for record in reader:
        if not record:
            continue
        match = re.match(r"\[row=(\d+)\]\s*(.*)", record[0])
        if not match:
            continue
        row_no = int(match.group(1))
        values = [match.group(2), *record[1:]]
        if len(values) < 4 or not values[0].strip():
            continue
        rows.append({
            "row": str(row_no),
            "name": values[0].strip(),
            "node_type": values[1].strip(),
        })
    return rows


def write_sheet_rows(url: str, sheet_id: str, rows: list[list[str]], start_cell: str, dry_run: bool) -> None:
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    cmd = [
        "lark-cli", "sheets", "+csv-put",
        "--url", url,
        "--sheet-id", sheet_id,
        "--start-cell", start_cell,
        "--csv", "-",
    ]
    if dry_run:
        cmd.append("--dry-run")
    _run_json(cmd, stdin=buf.getvalue())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_LARK_URL)
    parser.add_argument("--sheet-id", default=DEFAULT_SHEET_ID)
    parser.add_argument("--k8s-path", type=Path, default=DEFAULT_K8S_PATH)
    parser.add_argument("--storage-bucket", default=DEFAULT_STORAGE_BUCKET)
    parser.add_argument("--storage-prefix", default=DEFAULT_STORAGE_PREFIX)
    parser.add_argument("--skip-storage", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sheet_rows = read_sheet_rows(args.url, args.sheet_id)
    system_specs = load_system_specs(args.k8s_path)
    storage_specs = {} if args.skip_storage else load_storage_specs(args.storage_bucket, args.storage_prefix)
    specs = {**system_specs, **storage_specs}
    catalog = build_payload_catalog(specs)

    output_rows: list[list[str]] = []
    missing: list[str] = []
    for row in sheet_rows:
        spec = specs.get(row["name"])
        if not spec:
            missing.append(row["name"])
            output_rows.append(["", ""])
            continue
        mark_config_objects = spec.source.startswith("s3://")
        output_rows.append([
            render_params(spec.inputs, catalog, "No inputs", mark_config_objects),
            render_params(spec.outputs, catalog, "No outputs", mark_config_objects),
        ])

    if output_rows:
        write_sheet_rows(args.url, args.sheet_id, output_rows, "E2", args.dry_run)

    print(f"{'Would update' if args.dry_run else 'Updated'} {len(output_rows)} row(s) in input/output columns.")
    if missing:
        print("Missing definitions:")
        for name in missing:
            print(f"  - {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
