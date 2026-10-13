"""A local model handle. Reads from disk. No network."""
from __future__ import annotations

import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class Model(Protocol):
    id: str
    def generate(self, prompt: str, seed: int) -> str: ...


@dataclass
class FixtureModel:
    id: str
    fixtures: list[tuple] = field(default_factory=list)
    fallback: str = ""

    def generate(self, prompt: str, seed: int = 0) -> str:
        for needle, out in self.fixtures:
            if needle in prompt:
                return out
        return self.fallback


@dataclass
class DiskModel:
    id: str
    path: Path
    generate_fn: Callable[[str, int], str]

    def __post_init__(self):
        self.path = Path(self.path)

    @property
    def artifact_hash(self) -> str:
        if not self.path.exists():
            return "sha256:missing"
        h = hashlib.sha256()
        if self.path.is_file():
            h.update(self.path.read_bytes())
        else:
            for f in sorted(self.path.rglob("*")):
                if f.is_file():
                    h.update(str(f.relative_to(self.path)).encode())
                    h.update(f.read_bytes())
        return "sha256:" + h.hexdigest()[:24]

    def generate(self, prompt: str, seed: int = 0) -> str:
        return self.generate_fn(prompt, seed)


def mlx_model(path: str, model_id: str | None = None):
    """Local MLX-backed model. Never touches network."""
    try:
        from app.dispatch.models.local_mlx import LocalMLXProvider, _mlx_available
    except Exception:
        return None
    if not _mlx_available():
        return None
    prov = LocalMLXProvider(model_id or Path(path).stem, model_id=path)

    def _gen(prompt: str, seed: int) -> str:
        from app.dispatch.models.base import ModelRequest
        r = prov.complete(ModelRequest(task="coding", prompt=prompt,
                                       seed=seed, max_tokens=512,
                                       temperature=0.0))
        return r.text

    return DiskModel(id=model_id or Path(path).stem,
                     path=Path(path), generate_fn=_gen)
