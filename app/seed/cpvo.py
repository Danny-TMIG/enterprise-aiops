"""CPVO meter + record. Works with the manifest CPVORates."""
from __future__ import annotations

from app.seed.manifest import CPVORates, Manifest  # noqa: F401


class CPVORecord:
    def __init__(self, id: str = "", value: float = 0.0, **kwargs):
        self.id = id
        self.value = float(value)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)


class CPVOMeter:
    def __init__(self, rates: CPVORates | None = None, **kwargs):
        self.rates = rates or CPVORates()
        for k, v in kwargs.items():
            setattr(self, k, v)

    def measure(self, record) -> float:
        return float(record.value) * float(getattr(self.rates, "rate", 1.0))

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)
