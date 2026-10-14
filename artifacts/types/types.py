from __future__ import annotations

from typing import Protocol


class Service(Protocol):
    def handle(self, payload: dict) -> dict: ...
