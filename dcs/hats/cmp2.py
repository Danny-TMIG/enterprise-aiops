"""CMP2 — compliance. Self-attestation against the standard."""

import json
from pathlib import Path

from dcs.generate import requirement


def self_attest(std_path: Path, ev_path: Path) -> dict:
    std = json.loads(std_path.read_text())
    ev = json.loads(ev_path.read_text())
    return {
        "standard_ref": f"{std['standard']['id']}@{std['standard']['version']}",
        "verdict": ev.get("verdict"),
        "req_count": len(std.get("requirements", [])),
    }


@requirement(
    id="DCS-CMP2-001",
    title="compliance can reflect on its own standard",
    section="CMP2.compliance",
    hats=["CMP2"],
    criticality="MUST",
)
def test():
    root = Path(__file__).resolve().parent.parent.parent
    std = root / "dcs/standards/aiops.json"
    evs = sorted((root / "dcs/evidence").glob("run-*.json"))
    if not std.exists() or not evs:
        return  # nothing to attest yet
    r = self_attest(std, evs[-1])
    assert r["standard_ref"].startswith("dcs.aiops@")
