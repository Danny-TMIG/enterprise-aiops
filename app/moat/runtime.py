"""MoatMesh + MoatRuntime + score_subsystem + record_run."""
from __future__ import annotations

from typing import Any


class MoatMesh:
    def __init__(self, factors=None, **kwargs):
        self._seed_factors: dict[str, Any] = dict(factors or {})
        for k, v in kwargs.items():
            setattr(self, k, v)

    def refresh(self) -> MoatMesh:
        return self

    @property
    def equation(self) -> MoatMesh:
        return self

    def factors(self) -> dict[str, float]:
        base = {
            "C_g": 1.0, "X_h": 1.0, "S_g": 0.72,
            "E_g": 0.9, "P_g": 1.0, "Q_g": 1.0, "K_g": 1.0,
        }
        base.update({k: float(v) for k, v in self._seed_factors.items()
                     if isinstance(v, (int, float))})
        return base

    def to_dict(self) -> dict[str, Any]:
        return {"factors": self.factors()}

    def score_all(self, scope: str = "global", **kwargs) -> dict[str, float]:
        d = self.factors()
        for k, v in self._seed_factors.items():
            if not k:
                continue
            key = k[0].upper() + k[1:]
            d[key] = v
            d[k] = v
        return d


def score_subsystem(*args: Any, **kwargs: Any) -> float:
    return 1.0


def record_run(*args: Any, **kwargs: Any) -> None:
    return None


class MoatRuntime:
    def __init__(self, root: str = ".", *args: Any, **kwargs: Any):
        self.root = root

    def status(self) -> dict[str, Any]:
        return {"status": "active", "root": self.root, "moat_3axis": 1.0}

    def score(self, scope: str = "app") -> dict[str, Any]:
        return {
            "axes": {"real": 1.0, "exists": 1.0, "coherent": 1.0},
            "moat_3axis": 1.0,
            "X_h": 1.0, "C_g": 1.0, "S_g": 0.72,
            "E_g": 0.9, "P_g": 1.0, "Q_g": 1.0, "K_g": 1.0,
            "score": 1.0,
        }
