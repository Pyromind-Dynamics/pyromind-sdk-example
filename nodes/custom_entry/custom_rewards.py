"""GRPO reward functions.

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


# ──  奖励函数 ───────────────────────────────────────────────────


def thinking_reward(
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


def answer_reward(
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

 

if __name__ == "__main__":
    # Test thinking_reward
    test_completions_1 = [
        "Some irrelevant text <think>This is my detailed thinking process.</think>",
        "<think>Short</think>",
        "No think tag here.",
        "<think>     </think>",
    ]
    # Should reward 1 for long enough, 0 for short or empty
    print("thinking_reward:", thinking_reward(test_completions_1, min_thinking_chars=10))
    # Expect: [1.0, 0.0, 0.0, 0.0]

    # Test answer_reward
    test_completions_2 = [
        "The answer is <answer>A</answer>.",
        "<answer>B</answer>",
        "Random text <answer>C</answer>",
        "No answer here.",
    ]
    test_ground_truth = [
        "A",
        "B",
        "C",
        "D"
    ]
    print("answer_reward:", answer_reward(test_completions_2, test_ground_truth))
    # Expect: [1.0, 1.0, 1.0, 0.0]

    # Edge case: ground_truth shorter than completions
    print("answer_reward (short gt):", answer_reward(["<answer>A</answer>", "<answer>B</answer>"], ["A"]))
    # Expect: [1.0, 0.0] (since second gt will be empty string or None and not match)

    # Edge case: completions or gt are None or contain malformed tags
    print("answer_reward (malformed):", answer_reward([None, "<answer></answer>", "<answer>a</answer>"], ["A", "B", "a"]))
    # Expect: [0.0, 0.0, 1.0]