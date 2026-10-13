"""Derived from NIST SP 800-53 / NIST: AC Access."""
import json
from pathlib import Path
M = Path("dcs/standards/sdlc.json")
R = Path("dcs/standards/registry.json")

def test_sdlc_0821_clause_in_registry():
    data = json.loads(M.read_text())
    reg = json.loads(R.read_text())["registry"]
    proc = next(x for x in data["requirements"] if x["id"] == "SDLC-0821")
    std = proc["identity"]["standard"]
    assert std in reg, f"{std} not in registry"
    assert proc["identity"]["clause"] in reg[std]["clauses"], "clause not in registry"
    assert proc["controls"][0] in reg[std]["controls"], "control not in registry"
    assert proc["evidence"][0].endswith(tuple(reg[std]["evidence"])), "evidence not in registry"
    assert proc["state"] in {"UNKNOWN","TRUE","FALSE","CONFLICT"}
