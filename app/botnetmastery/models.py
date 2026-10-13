"""Canonical Bot and Task."""
from __future__ import annotations

import time
import uuid
from typing import Any


class Bot:
    def __init__(self, id: str | None = None,
                 hostname: str = "", os: str = "", arch: str = "",
                 last_seen: float = 0.0, status: str = "active"):
        self.id = id or str(uuid.uuid4())
        self.hostname = hostname
        self.os = os
        self.arch = arch
        self.last_seen = last_seen or time.time()
        self.status = status

    @property
    def bot_id(self) -> str:
        return self.id

    @classmethod
    def new(cls, hostname: str, os: str, arch: str,
            id: str | None = None) -> Bot:
        return cls(id=id, hostname=hostname, os=os, arch=arch)

    def __getitem__(self, key: str):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def __repr__(self) -> str:
        return f"Bot(id={self.id!r}, hostname={self.hostname!r})"


class Task:
    def __init__(self, id: str, bot_id: str, cmd: str,
                 args: dict[str, Any] | None = None,
                 status: str = "queued"):
        self.id = id
        self.bot_id = bot_id
        self.cmd = cmd
        self.args = dict(args or {})
        self.status = status

    @classmethod
    def new(cls, bot_id: str, cmd: str,
            args: dict[str, Any] | None = None) -> Task:
        return cls(id=str(uuid.uuid4()), bot_id=bot_id, cmd=cmd, args=args)

    def __getitem__(self, key: str):
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, bot={self.bot_id!r}, cmd={self.cmd!r})"


class BotModel:

    """A single simulated bot. In this codebase bots are inert:
    they hold state so the simulator can advance time, they never
    issue real network traffic.
    """
    def __init__(self, id: str = "", status: str = "idle", **kwargs):
        self.id = id
        self.status = status
        self.last_seen: float = 0.0
        self.commands: list = []
        self.metadata = kwargs

    def command(self, name: str) -> None:
        self.commands.append({"name": name, "accepted": self.status == "active"})

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "status": self.status,
            "last_seen": self.last_seen,
            "commands": list(self.commands),
            "metadata": dict(self.metadata),
        }

    def __repr__(self) -> str:
        return f"BotModel({self.id!r}, status={self.status!r})"

