from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Intent:
    raw: str
    channel: str = "cli"       # cli | api | git
    author: str = "user"
    target: str = ""           # file/route/module the intent touches
    ts: str = field(default_factory=_now)
    id: str = ""
    keywords: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.keywords:
            self.keywords = _keywords(self.raw)
        if not self.id:
            blob = f"{self.channel}:{self.author}:{self.raw}"
            self.id = "int-" + hashlib.sha256(blob.encode()).hexdigest()[:12]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "raw": self.raw, "channel": self.channel,
            "author": self.author, "target": self.target,
            "keywords": self.keywords, "ts": self.ts,
        }


_STOP = {
    "the", "a", "an", "to", "for", "of", "in", "on", "and", "or",
    "is", "are", "be", "with", "this", "that", "we", "i", "you",
}


def _keywords(text: str) -> list[str]:
    toks = re.findall(r"[A-Za-z0-9_/]+", text.lower())
    return [t for t in toks if t not in _STOP and len(t) >= 3]


def from_cli(text: str, target: str = "", author: str = "user") -> Intent:
    return Intent(raw=text, channel="cli", target=target, author=author)


def from_api(payload: dict[str, Any]) -> Intent:
    return Intent(
        raw=str(payload.get("intent", "")),
        channel="api",
        target=str(payload.get("target", "")),
        author=str(payload.get("author", "api")),
    )


def from_git(commit_msg: str, target: str = "", author: str = "git") -> Intent:
    return Intent(raw=commit_msg.strip(), channel="git",
                  target=target, author=author)
