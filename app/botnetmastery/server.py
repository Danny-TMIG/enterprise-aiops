import time
import uuid
from typing import Any


class Bot:
    def __init__(self, id: str, host: str, os: str, arch: str, status: str = "active", last_seen: float | None = None):
        self.id = id
        self.host = host
        self.os = os
        self.arch = arch
        self.status = status
        self.last_seen = last_seen or time.time()
        self._data = {
            "id": self.id,
            "host": self.host,
            "os": self.os,
            "arch": self.arch,
            "status": self.status,
            "last_seen": self.last_seen
        }

    @classmethod
    def new(cls, host: str, os: str, arch: str) -> "Bot":
        bot_id = f"bot-{uuid.uuid4().hex[:8]}"
        return cls(id=bot_id, host=host, os=os, arch=arch)

    def __getitem__(self, key: str) -> Any:
        if key in self._data:
            return self._data[key]
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Bot has no attribute '{key}'")

    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
        if hasattr(self, key):
            setattr(self, key, value)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def update_status(self, status: str):
        self.status = status
        self._data["status"] = status
        self.last_seen = time.time()
        self._data["last_seen"] = self.last_seen


class Task:
    def __init__(self, id: str, bot_id: str, command: str, args: dict[str, Any], status: str = "pending", result: Any | None = None):
        self.id = id
        self.bot_id = bot_id
        self.command = command
        self.args = args
        self.status = status
        self.result = result
        self._data = {
            "id": self.id,
            "bot_id": self.bot_id,
            "command": self.command,
            "args": self.args,
            "status": self.status,
            "result": self.result
        }

    @classmethod
    def new(cls, bot_id: str, command: str, args: dict[str, Any]) -> "Task":
        task_id = f"task-{uuid.uuid4().hex[:8]}"
        return cls(id=task_id, bot_id=bot_id, command=command, args=args)

    def __getitem__(self, key: str) -> Any:
        if key in self._data:
            return self._data[key]
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Task has no attribute '{key}'")

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default


class C2Server:
    def __init__(self, db_path: str = "botnet.db", *args: Any, **kwargs: Any):
        self.db_path = db_path
        self.bots: dict[str, Bot] = {}
        self.tasks: dict[str, Task] = {}
        self.kill_switch_engaged = False
        self.killed = False

    def register_bot(self, bot: Bot) -> None:
        self.bots[bot.id] = bot

    def get_bot(self, bot_id: str) -> Bot:
        if bot_id not in self.bots:
            raise KeyError(f"Bot {bot_id} not found")
        return self.bots[bot_id]

    def queue_task(self, *args: Any, **kwargs: Any) -> Any:
        if self.kill_switch_engaged or self.killed:
            raise RuntimeError("Kill switch engaged: cannot queue tasks.")
        
        if len(args) == 1 and isinstance(args[0], Task):
            task = args[0]
        else:
            bot_id = kwargs.get("bot_id") or (args[0] if len(args) > 0 else "unknown")
            command = kwargs.get("command") or (args[1] if len(args) > 1 else "unknown")
            task_args = kwargs.get("args") or (args[2] if len(args) > 2 else {})
            task = Task.new(bot_id=bot_id, command=command, args=task_args)

        self.tasks[task.id] = task
        return {"task_id": task.id, "bot_id": task.bot_id, "command": task.command}

    def dispatch_next(self, bot_id: str) -> Task | None:
        if self.kill_switch_engaged or self.killed:
            return None
        for task in self.tasks.values():
            if task.bot_id == bot_id and task.status == "pending":
                task.status = "dispatched"
                task._data["status"] = "dispatched"
                return task
        return None

    def complete_task(self, task_id: str, result: Any) -> None:
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = "completed"
            task.result = result
            task._data["status"] = "completed"
            task._data["result"] = result

    def pending_tasks(self, bot_id: str) -> list[Task]:
        return [t for t in self.tasks.values() if t.bot_id == bot_id and t.status in ("pending", "dispatched")]

    def heartbeat(self, bot_id: str) -> None:
        if bot_id in self.bots:
            self.bots[bot_id].update_status("active")

    def engage_kill_switch(self, reason: str = "manual") -> dict[str, Any]:
        self.kill_switch_engaged = True
        self.killed = True
        for bot in self.bots.values():
            bot.update_status("terminated")
        for task in self.tasks.values():
            if task.status in ("pending", "dispatched"):
                task.status = "revoked"
                task._data["status"] = "revoked"
        return {"status": "terminated", "reason": reason}

    def revoke_all_commands(self) -> int:
        count = 0
        for task in self.tasks.values():
            if task.status in ("pending", "dispatched"):
                task.status = "revoked"
                task._data["status"] = "revoked"
                count += 1
        return count


class Simulation:
    def __init__(self, srv: C2Server, seed: int = 1, *args: Any, **kwargs: Any):
        self.srv = srv
        self.seed = seed
        self.spawned_bots: list[Bot] = []
        self.broadcast_queue: list[dict[str, Any]] = []

    def spawn(self, n: int) -> list[Bot]:
        bots = []
        for i in range(n):
            b = Bot.new(f"host-{i}", "linux", "x86_64")
            self.srv.register_bot(b)
            self.spawned_bots.append(b)
            bots.append(b)
        return bots

    def queue_broadcast(self, *args: Any, **kwargs: Any) -> Any:
        action = kwargs.get("action") or kwargs.get("cmd") or (args[0] if len(args) > 0 else "broadcast")
        payload = kwargs.get("payload") or kwargs.get("args") or (args[1] if len(args) > 1 else {})
        self.broadcast_queue.append({"action": action, "payload": payload})
        task_ids = []
        for b in self.spawned_bots:
            t = Task.new(b.id, action, payload)
            tid = self.srv.queue_task(t)
            task_ids.append(tid)
        return task_ids

    def tick(self) -> None:
        if self.srv.kill_switch_engaged or self.srv.killed:
            return
        for b in self.spawned_bots:
            self.srv.heartbeat(b.id)


try:
    from fastapi import FastAPI as _FastAPI
except ImportError:
    _FastAPI = None
app = _FastAPI(title="app") if _FastAPI else None
