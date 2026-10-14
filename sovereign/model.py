"""Model backend for the sovereign node.

Lazy-loaded. If a model path exists and mlx_lm is installed, the node
serves a real model. If not, it falls back to a deterministic echo so
the pipeline (ledger, wire format, hashing) still runs end to end.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_CACHE: dict[str, Any] = {}


def _load(model_path: Path):
    """Load once, cache forever. Raise if unavailable."""
    key = str(model_path)
    if key in _CACHE:
        return _CACHE[key]

    from mlx_lm import load
    model, tokenizer = load(str(model_path))
    _CACHE[key] = (model, tokenizer)
    return _CACHE[key]


def generate(
    model_path: Path,
    messages: list[dict[str, str]],
    max_tokens: int = 256,
) -> tuple[str, int, int]:
    """Return (content, prompt_tokens, completion_tokens).

    Real backend if mlx_lm and a model are available. Echo fallback
    otherwise so the pipeline is always testable.
    """
    # Try the real backend
    if model_path.exists():
        try:
            model, tokenizer = _load(model_path)
            from mlx_lm import generate as mlx_generate

            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True,
            )
            content = mlx_generate(
                model, tokenizer, prompt=prompt, max_tokens=max_tokens,
            )
            prompt_tokens = len(tokenizer.encode(prompt))
            completion_tokens = len(tokenizer.encode(content))
            return content, prompt_tokens, completion_tokens
        except Exception as e:
            # Fall through to echo, but record the reason
            reason = f"{type(e).__name__}: {e}"
    else:
        reason = f"model path does not exist: {model_path}"

    # Echo fallback — the pipeline runs, the response says why
    prompt_text = " ".join(m.get("content", "") for m in messages)
    content = f"[sovereign echo] backend unavailable ({reason})"
    return content, max(1, len(prompt_text) // 4), max(1, len(content) // 4)
