"""Append-only registry for governance primitives.

Records are never mutated in place. Revocation is a new record.
The registry is a JSONL file so that history is the registry.
"""
from __future__ import annotations
import json, os, threading
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from app.agency.primitives import (
    Agency, License, Certification, Expertise,
)

_DEFAULT = Path(".agency/registry.jsonl")
_LOCK = threading.Lock()
_INSTANCE: Optional["Registry"] = None


def _to_obj(kind: str, d: Dict[str, Any]):
    d = {k: v for k, v in d.items() if k != "kind"}
    if kind == "agency":
        return Agency(**d)
    if kind == "license":
        return License(**d)
    if kind == "cert":
        return Certification(**d)
    if kind == "expertise":
        return Expertise(**d)
    raise ValueError(f"unknown kind: {kind}")


def _to_record(obj) -> Dict[str, Any]:
    d = asdict(obj)
    d["kind"] = obj.__class__.__name__.lower()
    if isinstance(obj, Certification):
        d["kind"] = "cert"
    return d


class Registry:
    def __init__(self, path: Path = _DEFAULT):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    # ── write ────────────────────────────────────────────────────
    def append(self, obj) -> str:
        with _LOCK:
            with self.path.open("a") as f:
                f.write(json.dumps(_to_record(obj)) + "\n")
        return getattr(obj, "id", "")

    def revoke(self, kind: str, id_: str, by: str, reason: str) -> None:
        with _LOCK:
            with self.path.open("a") as f:
                f.write(json.dumps({
                    "kind": "revocation",
                    "target_kind": kind,
                    "target_id": id_,
                    "by": by,
                    "reason": reason,
                }) + "\n")

    # ── read ─────────────────────────────────────────────────────
    def _load(self) -> List[Dict[str, Any]]:
        out = []
        for line in self.path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
        return out

    def all(self) -> Dict[str, List[Any]]:
        rows = self._load()
        revoked: Dict[str, set] = {}
        for r in rows:
            if r.get("kind") == "revocation":
                revoked.setdefault(r["target_kind"], set()).add(r["target_id"])

        out: Dict[str, List[Any]] = {
            "agency": [], "license": [], "cert": [], "expertise": [],
        }
        # expertise accumulates across records for the same subject+domain
        exp_acc: Dict[str, Expertise] = {}

        for r in rows:
            k = r.get("kind")
            if k in ("agency", "license", "cert"):
                obj = _to_obj(k, r)
                if obj.id in revoked.get(k, set()):
                    obj = obj.__class__(**{**obj.__dict__, "revoked": True})
                out[k].append(obj)
            elif k == "expertise":
                key = (r["subject"], r["domain"])
                if key not in exp_acc:
                    exp_acc[key] = _to_obj("expertise", r)
                else:
                    acc = exp_acc[key]
                    acc.completions = max(acc.completions, r["completions"])
                    acc.successes = max(acc.successes, r["successes"])
                    acc.failures = max(acc.failures, r["failures"])
                    acc.last_updated = r["last_updated"]
                    acc.evidence_hashes = r.get("evidence_hashes", [])
        out["expertise"] = list(exp_acc.values())
        return out

    def for_subject(self, subject: str) -> Dict[str, List[Any]]:
        everything = self.all()
        return {k: [r for r in v if getattr(r, "subject", None) == subject]
                for k, v in everything.items()}


def get_registry(path: Optional[str] = None) -> Registry:
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = Registry(Path(path) if path else _DEFAULT)
    return _INSTANCE


class AgencyRegistry:

    """In-memory index of named primitives.

    Distinct from `Registry` in the same module: `Registry` is the
    append-only JSONL log; `AgencyRegistry` is a working-set cache
    keyed by name or id, suitable for lookups during gate evaluation.
    """
    def __init__(self, initial=None):
        self._items: dict = {}
        if initial:
            for k, v in initial.items():
                self.register(k, v)

    def register(self, key: str, value=None) -> object:
        """Insert an entry. If `value` is None, `key` must be the record."""
        if value is None:
            value = key
            key = getattr(value, "name", None) or getattr(value, "id", "")
        self._items[key] = value
        return value

    def unregister(self, key: str) -> object | None:
        return self._items.pop(key, None)

    def get(self, key: str, default=None):
        return self._items.get(key, default)

    def all(self) -> dict:
        return dict(self._items)

    def __contains__(self, key: str) -> bool:
        return key in self._items

    def __len__(self) -> int:
        return len(self._items)

