"""Staging — atomic patches with snapshot + rollback."""
from __future__ import annotations

import difflib
import shutil
import time
from pathlib import Path


class Staging:
    def __init__(self, root: str = ".") -> None:
        self.root = Path(root).resolve()
        self.stage_dir = self.root / ".meta_stage"
        self.history_dir = self.stage_dir / "history"
        self.stage_dir.mkdir(exist_ok=True)
        self.history_dir.mkdir(exist_ok=True)

    def _real(self, target: str) -> Path:
        return self.root / target

    def _staged(self, target: str) -> Path:
        p = self.stage_dir / target
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _snapshot_dir(self, target: str) -> Path:
        ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
        d = self.history_dir / ts
        d.mkdir(parents=True, exist_ok=True)
        (d / "target.txt").write_text(target)
        return d

    def propose(self, target: str, new_source: str) -> Path:
        p = self._staged(target)
        p.write_text(new_source)
        return p

    def has_proposal(self, target: str) -> bool:
        return self._staged(target).exists()

    def diff(self, target: str) -> str:
        real = self._real(target)
        staged = self._staged(target)
        if not staged.exists():
            return "<no proposal>"
        old_lines = real.read_text().splitlines(keepends=True) if real.exists() else []
        new_lines = staged.read_text().splitlines(keepends=True)
        return "".join(difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"a/{target}", tofile=f"b/{target}",
        ))

    def staged_source(self, target: str) -> str | None:
        p = self._staged(target)
        return p.read_text() if p.exists() else None

    def apply(self, target: str) -> Path:
        real = self._real(target)
        staged = self._staged(target)
        if not staged.exists():
            raise FileNotFoundError(f"no staged proposal for {target}")
        snap = self._snapshot_dir(target)
        if real.exists():
            shutil.copy2(real, snap / "original")
        shutil.copy2(staged, real)
        return snap

    def rollback(self, target: str, snapshot: Path) -> None:
        real = self._real(target)
        orig = snapshot / "original"
        if orig.exists():
            shutil.copy2(orig, real)
        elif real.exists():
            real.unlink()

    def revert(self, target: str) -> None:
        p = self._staged(target)
        if p.exists():
            p.unlink()
