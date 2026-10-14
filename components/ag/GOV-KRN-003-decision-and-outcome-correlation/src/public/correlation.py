"""GOV-KRN-003: Decision and outcome correlation registry."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


class CorrelationError(Exception): ...
class AlreadyOpenError(CorrelationError): ...
class AlreadyClosedError(CorrelationError): ...
class UnknownCorrelationError(CorrelationError): ...


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Correlation:
    correlation_id: str
    decision_refs: list[str]
    status: str = "OPEN"
    outcome_ref: str | None = None
    opened_at: str = field(default_factory=_now)
    closed_at: str | None = None


class CorrelationRegistry:
    def __init__(self) -> None:
        self._records: dict[str, Correlation] = {}

    def __enter__(self) -> "CorrelationRegistry":
        return self

    def __exit__(self, *exc: object) -> None:
        self._records.clear()

    def open(self, correlation_id: str, decision_refs: list[str]) -> Correlation:
        if not decision_refs:
            raise CorrelationError("at least one decision ref is required")
        if correlation_id in self._records:
            raise AlreadyOpenError(f"correlation already open: {correlation_id}")
        rec = Correlation(correlation_id, list(decision_refs))
        self._records[correlation_id] = rec
        return rec

    def close_with_outcome(self, correlation_id: str, outcome_ref: str) -> Correlation:
        rec = self._records.get(correlation_id)
        if rec is None:
            raise UnknownCorrelationError(f"unknown correlation: {correlation_id}")
        if rec.status == "CLOSED":
            raise AlreadyClosedError(f"correlation already closed: {correlation_id}")
        rec.status = "CLOSED"
        rec.outcome_ref = outcome_ref
        rec.closed_at = _now()
        return rec

    def get(self, correlation_id: str) -> Correlation:
        rec = self._records.get(correlation_id)
        if rec is None:
            raise UnknownCorrelationError(f"unknown correlation: {correlation_id}")
        return rec

    def open_correlations(self) -> list[str]:
        return sorted(cid for cid, rec in self._records.items() if rec.status == "OPEN")
