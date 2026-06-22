"""Geometry VQA GRPO reward functions.

Dataset ``gt`` and model completions use:
``<think>...</think>\\n\\n<answer>X</answer>``
"""

from __future__ import annotations

import re
from typing import Any

_ANSWER_RE = re.compile(r"<answer>\s*(.*?)\s*</answer>", flags=re.DOTALL | re.IGNORECASE)
_THINK_RE = re.compile(r"<think>(.*?)</think>", flags=re.DOTALL)
DEFAULT_MIN_THINKING_CHARS = 20


def _flatten_completions(completions: list[Any]) -> list[str]:
    flat: list[str] = []
    for c in completions:
        if isinstance(c, list):
            for item in c:
                if isinstance(item, dict) and "content" in item:
                    flat.append(str(item["content"]))
                else:
                    flat.append(str(item))
        elif isinstance(c, dict) and "content" in c:
            flat.append(str(c["content"]))
        else:
            flat.append(str(c))
    return flat


def _normalize_ground_truth(ground_truth: Any, n: int) -> list[str]:
    if ground_truth is None:
        return [""] * n
    if isinstance(ground_truth, list):
        if len(ground_truth) == n:
            return ["" if g is None else str(g) for g in ground_truth]
        if len(ground_truth) == 1 and n > 1:
            return ["" if ground_truth[0] is None else str(ground_truth[0])] * n
    return [str(ground_truth)] * n


def extract_answer_letter(text: str) -> str | None:
    """Extract the last ``<answer>...</answer>`` payload, normalized to uppercase."""
    if not isinstance(text, str):
        return None
    matches = _ANSWER_RE.findall(text)
    if not matches:
        return None
    payload = matches[-1].strip()
    if not payload:
        return None
    # Multiple-choice labels are single letters; keep first token for robustness.
    token = payload.split()[0].strip().upper()
    return token or None


def extract_last_thinking_inner(text: str) -> str | None:
    """Return inner text of the last ``<think>...</think>`` block."""
    if not isinstance(text, str):
        return None
    matches = _THINK_RE.findall(text)
    if not matches:
        return None
    inner = matches[-1].strip()
    return inner or None


def geometry_vqa_thinking_reward(
    completions: list[Any],
    ground_truth: list[str] | None = None,  # noqa: ARG001
    min_thinking_chars: int = DEFAULT_MIN_THINKING_CHARS,
    **kwargs: Any,
) -> list[float]:
    """Reward 1.0 when the last thinking block is non-empty and long enough."""
    del kwargs
    flat = _flatten_completions(completions)
    min_len = max(int(min_thinking_chars), 1)
    scores: list[float] = []
    for comp in flat:
        inner = extract_last_thinking_inner(comp)
        scores.append(1.0 if inner is not None and len(inner) > min_len else 0.0)
    return scores


def geometry_vqa_answer_reward(
    completions: list[Any],
    ground_truth: list[str] | None = None,
    **kwargs: Any,
) -> list[float]:
    """Reward 1.0 when predicted answer letter matches ``ground_truth``."""
    del kwargs
    flat = _flatten_completions(completions)
    gts = _normalize_ground_truth(ground_truth, len(flat))
    scores: list[float] = []
    for comp, gt in zip(flat, gts):
        pred = extract_answer_letter(comp)
        ref = extract_answer_letter(gt)
        scores.append(1.0 if pred is not None and ref is not None and pred == ref else 0.0)
    return scores


def geometry_vqa_answer_format_reward(
    completions: list[Any],
    ground_truth: list[str] | None = None,  # noqa: ARG001
    **kwargs: Any,
) -> list[float]:
    """Reward 1.0 when completion contains a non-empty ``<answer>`` block."""
    del kwargs
    flat = _flatten_completions(completions)
    return [1.0 if extract_answer_letter(comp) is not None else 0.0 for comp in flat]


def make_geometry_vqa_reward_length(max_completion_length: int = 1024):
    """Factory: token-length penalty aligned with ``--max_completion_length``.

    ``length_ref = max_completion_length / 16``; scores in approximately ``[-2.0, 0]``.
    """
    length_ref = max_completion_length // 16
    length_max = max_completion_length

    def reward_length(
        completions: list[Any],
        ground_truth: list[str] | None = None,  # noqa: ARG001
        completion_ids: list[Any] | None = None,
        **kwargs: Any,
    ) -> list[float]:
        del kwargs
        scores: list[float] = []
        completion_ids = completion_ids or []
        if len(completion_ids) != len(completions):
            raise AssertionError("completion_ids 与 completions 长度须一致")
        for ids in completion_ids:
            token_len = ids.numel() if hasattr(ids, "numel") else len(ids)
            ratio = (token_len - length_ref) / max(length_max - length_ref, 1)
            ratio = min(max(ratio, 0.0), 1.0)
            if ratio < 0.75:
                scores.append(-0.3 * ratio)
            else:
                scores.append(-2.0 * ratio)
        return scores

    return reward_length
