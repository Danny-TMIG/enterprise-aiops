#!/usr/bin/env python3
"""Generative + parallel type constructor writer."""

from __future__ import annotations

import itertools
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

NOUNS = [
    "State",
    "Event",
    "Record",
    "Claim",
    "Proof",
    "Witness",
    "Grant",
    "Receipt",
    "Envelope",
    "Policy",
    "Capability",
    "Approval",
    "Outcome",
    "Directive",
    "Ledger",
    "Digest",
    "Schema",
    "Bundle",
    "Manifest",
    "Attestation",
    "Identity",
    "Authority",
    "Consent",
    "Revocation",
    "Decision",
    "Evidence",
    "Signal",
    "Operation",
    "Outbox",
    "Registry",
]

VERBS = [
    "",
    "Create",
    "Update",
    "Verify",
    "Sign",
    "Seal",
    "Revoke",
    "Approve",
    "Reject",
    "Publish",
    "Consume",
    "Emit",
]

SUFFIXES = [
    "",
    "Request",
    "Response",
    "Result",
    "Error",
    "Spec",
    "Ref",
    "Record",
    "View",
    "Summary",
    "Detail",
]

TEMPLATE = '''"""Auto-generated type constructor: {name}."""
from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field, asdict


@dataclass
class {name}:
    name: str
    payload: dict = field(default_factory=dict)
    ts: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

    def digest(self) -> str:
        canon = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canon.encode()).hexdigest()


__all__ = ["{name}"]
'''


def sanitize(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_]", "_", s)
    if not s or not s[0].isalpha():
        s = "T_" + s
    return s


def emit(args):
    out, name = args
    p = Path(out) / (name + ".py")
    if p.exists():
        return name, False
    try:
        p.write_text(TEMPLATE.format(name=name))
        return name, True
    except Exception as e:
        return name, repr(e)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "constructors/generated"
    Path(out).mkdir(parents=True, exist_ok=True)

    jobs = []
    seen = set()
    for n, v, s in itertools.product(NOUNS, VERBS, SUFFIXES):
        name = sanitize(n + v + s)
        if name in seen:
            continue
        seen.add(name)
        jobs.append((out, name))

    print("generating", len(jobs), "constructors into", out)

    written = skipped = failed = 0
    with ProcessPoolExecutor(max_workers=16) as pool:
        for fut in as_completed([pool.submit(emit, j) for j in jobs]):
            name, res = fut.result()
            if res is True:
                written += 1
            elif res is False:
                skipped += 1
            else:
                failed += 1
                print("  FAIL", name, res)

    names = sorted(n for _, n in jobs)
    init = Path(out) / "__init__.py"
    init.write_text(
        "".join(f"from .{n} import {n}\n" for n in names) + "\n__all__ = " + repr(names) + "\n"
    )
    print("wrote", init)
    print(f"summary: written={written} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
