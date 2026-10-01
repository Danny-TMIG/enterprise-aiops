"""Semver range matching, IETF-style."""
from dcs.generate import requirement

import re
_VER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

def parse(v): 
    m = _VER.match(v); return tuple(map(int, m.groups())) if m else None

def satisfies(version: str, spec: str) -> bool:
    v = parse(version)
    if v is None: return False
    if spec.startswith("^"):
        lo = parse(spec[1:])
        return lo <= v < (lo[0]+1, 0, 0)
    if spec.startswith("~"):
        lo = parse(spec[1:])
        return lo <= v < (lo[0], lo[1]+1, 0)
    return parse(spec) == v

@requirement(id="DCS-XC-SEMVER-001", title="caret/tilde/exact match correctly",
             section="X.semver", hats=["REL", "PL"], criticality="MUST")
def test():
    assert satisfies("1.2.3", "^1.0.0")
    assert not satisfies("2.0.0", "^1.0.0")
    assert satisfies("1.2.9", "~1.2.0")
    assert not satisfies("1.3.0", "~1.2.0")
    assert satisfies("1.2.3", "1.2.3")
