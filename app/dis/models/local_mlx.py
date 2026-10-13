"""Local MLX backend: Apple Silicon inference via mlx-lm.

Importable even when mlx is not installed; `load()` and `generate()`
degrade gracefully and report `loaded=False`.
"""
from __future__ import annotations

from typing import Any


class LocalMLX:
    """Wrapper around mlx-community models for on-device inference."""

    def __init__(self, model_id: str = "mlx-community/Qwen2.5-7B-Instruct-4bit"):
        self.model_id = model_id
        self._model: Any = None
        self._tokenizer: Any = None

    def load(self) -> bool:
        try:
            import mlx_lm
        except ImportError:
            self._model = None
            return False
        import mlx_lm
        self._model, self._tokenizer = mlx_lm.load(self.model_id)
        return True

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        if self._model is None:
            return ""
        import mlx_lm
        return mlx_lm.generate(
            self._model, self._tokenizer,
            prompt=prompt, max_tokens=max_tokens,
        )

    @property
    def loaded(self) -> bool:
        return self._model is not None


def load_local_mlx(model_id: str = "mlx-community/Qwen2.5-7B-Instruct-4bit") -> LocalMLX:
    backend = LocalMLX(model_id)
    backend.load()
    return backend
