"""Loads generated skip rules. Regenerate by rerunning skip_generator."""

from __future__ import annotations

import json
from pathlib import Path

_RULES = None


def load_rules(root: Path | None = None) -> dict:
    global _RULES
    if _RULES is None:
        root = root or Path.cwd()
        p = root / "atlas_naming" / "skip_rules.json"
        if not p.exists():
            raise FileNotFoundError(f"missing {p}; run skip_generator first")
        _RULES = json.loads(p.read_text())
    return _RULES


def is_skipped(path: Path, root: Path | None = None) -> bool:
    root = root or Path.cwd()
    rules = load_rules(root)
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return False
    if path.is_file():
        info = rules["file_decisions"].get(rel)
        if info is None:
            # File was not classified because parent was already skipped
            for ancestor_rel, ancestor_info in rules["directory_decisions"].items():
                if rel.startswith(ancestor_rel + "/") and ancestor_info["decision"] == "skip":
                    return True
            return False
        return info["decision"] == "skip"
    info = rules["directory_decisions"].get(rel)
    if info is None:
        return False
    return info["decision"] == "skip"
