"""通用评估指标插件，供 ``train/eval_model_api.py`` 的 ``--metrics-entry`` 使用。

每个指标导出独立可调用函数，通过 ``path/to/file.py:function_name`` 加载，并配合
``--metrics-name`` 指定聚合字段名。
"""

from __future__ import annotations

from ast import main
import re
from typing import Any

# ── 文本规范化 ────────────────────────────────────────────────────────────────

_WHITESPACE_RE = re.compile(r"\s+")
_NUMBER_RE = re.compile(r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")
_GSM8K_BOXED_RE = re.compile(r"\\boxed\{([^}]+)\}")
_GSM8K_ANSWER_TAG_RE = re.compile(
    r"<answer>\s*(.*?)\s*</answer>",
    re.IGNORECASE | re.DOTALL,
)


def _metric_key(metrics_name: str | None, default: str) -> str:
    key = (metrics_name or "").strip()
    return key or default


def _normalize_whitespace(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text.strip())


def _normalize_number(text: str) -> str | None:
    """将数字字符串规范为可比较的 canonical 形式。"""
    raw = text.strip().replace(",", "").replace("$", "").replace("%", "")
    if not raw:
        return None
    m = _NUMBER_RE.search(raw)
    if not m:
        return None
    num = m.group(0).replace(",", "")
    try:
        val = float(num)
    except ValueError:
        return num
    if val.is_integer():
        return str(int(val))
    return str(val).rstrip("0").rstrip(".") if "." in str(val) else str(val)


def extract_gsm8k_answer(text: str) -> str | None:
    """从 GSM8K 风格文本中提取最终数值答案。

    优先级：``####`` 后缀 > ``\\boxed{}`` > ``<answer>`` 标签 > 文中最后一个数字。
    """
    text = text.strip()
    if not text:
        return None

    if "####" in text:
        tail = text.rsplit("####", 1)[-1].strip()
        norm = _normalize_number(tail)
        if norm is not None:
            return norm
        return _normalize_whitespace(tail)

    boxed = _GSM8K_BOXED_RE.search(text)
    if boxed:
        norm = _normalize_number(boxed.group(1))
        if norm is not None:
            return norm

    tag = _GSM8K_ANSWER_TAG_RE.search(text)
    if tag:
        norm = _normalize_number(tag.group(1))
        if norm is not None:
            return norm

    numbers = _NUMBER_RE.findall(text.replace(",", ""))
    if numbers:
        norm = _normalize_number(numbers[-1])
        if norm is not None:
            return norm

    return _normalize_whitespace(text)


def _result(score: float, metrics_name: str | None, default_key: str, **extra: Any) -> dict:
    key = _metric_key(metrics_name, default_key)
    out: dict[str, Any] = {key: float(score)}
    out.update(extra)
    return out


# ── eval_model_api 指标函数 ───────────────────────────────────────────────────

def compute_gsm8k(
    gt_text: str,
    pred_text: str,
    sample: dict,
    *,
    metrics_name: str | None = None,
) -> dict | None:
    """GSM8K 数值答案准确率：提取并比较最终数字答案。"""
    gt_ans = extract_gsm8k_answer(gt_text)
    pred_ans = extract_gsm8k_answer(pred_text)
    if gt_ans is None:
        return None
    if pred_ans is None:
        return _result(0.0, metrics_name, "gsm8k", gt_answer=gt_ans, pred_answer="")
    score = 1.0 if gt_ans == pred_ans else 0.0
    return _result(score, metrics_name, "gsm8k", gt_answer=gt_ans, pred_answer=pred_ans)


if __name__ == "__main__":
    result = compute_gsm8k("#### 123", "\\boxed{123}", {}, metrics_name="acc")
    print(result)