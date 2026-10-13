"""Parse CodeQL SARIF into mesh nodes."""
from __future__ import annotations

import json
from pathlib import Path


def parse_sarif(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    try:
        d = json.loads(p.read_text())
    except Exception:
        return []
    out: list[dict] = []
    for run in d.get("runs", []):
        for res in run.get("results", []):
            rule = res.get("ruleId", "")
            msg = res.get("message", {}).get("text", "")
            locs = res.get("locations", [])
            file = ""
            line = 0
            if locs:
                pl = locs[0].get("physicalLocation", {})
                file = pl.get("artifactLocation", {}).get("uri", "")
                line = int(pl.get("region", {}).get("startLine", 0) or 0)
            parts = msg.split("|")
            if not parts:
                continue
            kind = parts[0].strip() or rule.rsplit("/", 1)[-1]
            name = parts[1].strip() if len(parts) > 1 else ""
            extra = [p.strip() for p in parts[2:] if p.strip()]
            out.append({
                "kind": kind,
                "name": name,
                "file": file,
                "line": line,
                "extra": extra,
                "rule": rule,
            })
    return out
