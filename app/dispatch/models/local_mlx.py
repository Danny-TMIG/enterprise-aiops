"""Local MLX provider for Apple silicon.

Loads a model from the Hugging Face cache (or downloads once) and
generates tokens in-process. No API key, no network at call time
once the weights are cached.

Env overrides:
    MLX_MODEL       default model id (default: Qwen2.5-7B-Instruct-4bit)
    MLX_MAX_TOKENS  default max_tokens per call (default: 256)
    MLX_DISABLE     set to 1 to force the provider off
"""
from __future__ import annotations

import os
import threading
from typing import Any

from app.dispatch.models.base import ModelRequest, ModelResponse

DEFAULT_MODEL = "mlx-community/Qwen2.5-7B-Instruct-4bit"

# process-wide cache so multiple provider aliases share the model
_LOCK = threading.Lock()
_CACHE: dict[str, Any] = {"model": None, "tokenizer": None,
                          "model_id": None}


def _mlx_available() -> bool:
    if os.environ.get("MLX_DISABLE") == "1":
        return False
    try:
        import mlx.core  # noqa: F401
        import mlx_lm  # noqa: F401
        return True
    except Exception:
        return False


def _load(model_id: str):
    with _LOCK:
        if _CACHE["model"] is not None and _CACHE["model_id"] == model_id:
            return _CACHE["model"], _CACHE["tokenizer"]
        from mlx_lm import load
        model, tokenizer = load(model_id)
        _CACHE["model"] = model
        _CACHE["tokenizer"] = tokenizer
        _CACHE["model_id"] = model_id
        return model, tokenizer


class LocalMLXProvider:
    """One local provider, multiple vendor aliases."""

    def __init__(self, alias: str, model_id: str | None = None) -> None:
        self.name = alias
        self._model_id = model_id or os.environ.get("MLX_MODEL", DEFAULT_MODEL)
        self.default_model = self._model_id

    def available(self) -> bool:
        return _mlx_available()

    def _call(self, req: ModelRequest) -> ModelResponse:
        from mlx_lm import generate
        model_id = req.metadata.get("model") or self._model_id
        model, tokenizer = _load(model_id)

        # Build a single prompt from system + user messages.
        system = req.system or "You are a mesh worker."
        prompt = (
            f"<|im_start|>system\n{system}<|im_end|>\n"
            f"<|im_start|>user\n{req.prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        max_tokens = int(req.metadata.get(
            "max_tokens", os.environ.get("MLX_MAX_TOKENS", req.max_tokens)))
        max_tokens = min(max_tokens, req.max_tokens or 256)

        text = generate(
            model, tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            verbose=False,
        )
        # MLX returns the completion only; approximate token usage.
        in_tok = len(tokenizer.encode(prompt))
        out_tok = len(tokenizer.encode(text))
        return ModelResponse(
            provider=self.name,
            model=model_id,
            text=text.strip(),
            usage={"input_tokens": in_tok, "output_tokens": out_tok},
            raw={"backend": "mlx", "local": True},
            dry_run=False,
        )
