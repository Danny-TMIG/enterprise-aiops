"""Human gate — accept, reject, or edit a staged patch."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path


def review(target: str, diff: str, before, staged_path: Path,
           auto: str | None = None) -> str:
    """Return 'accept', 'reject', or 'edit'.

    `auto` may be set to 'accept' or 'reject' to bypass the prompt
    for tests.
    """
    if auto in ("accept", "reject", "edit"):
        return auto

    print()
    print("═" * 60)
    print(f"  proposed patch → {target}")
    print("═" * 60)
    print(f"  before: mean={before.mean:.3f}  "
          f"axis_pass={before.axis_pass}")
    print()
    print(diff[:4000])
    if len(diff) > 4000:
        print(f"  ... ({len(diff) - 4000} more diff chars)")
    print()
    while True:
        try:
            ans = input("  [a]ccept  [r]eject  [e]dit  [s]kip: ").strip().lower()
        except EOFError:
            return "reject"
        if ans in ("a", "accept"):
            return "accept"
        if ans in ("r", "reject"):
            return "reject"
        if ans in ("e", "edit"):
            editor = os.environ.get("EDITOR", "vi")
            subprocess.call([editor, str(staged_path)])
            return "edit"
        if ans in ("s", "skip"):
            return "reject"


def edit(staged_path: Path) -> str:
    editor = os.environ.get("EDITOR", "vi")
    subprocess.call([editor, str(staged_path)])
    return staged_path.read_text()
