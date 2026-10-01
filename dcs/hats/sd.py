"""SD — sec defensive. Input allowlist."""
import re
from dcs.generate import requirement

OK = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")

def safe_name(s: str) -> str:
    if not OK.fullmatch(s): raise ValueError(f"unsafe name: {s!r}")
    return s

@requirement(id="DCS-SD-001", title="allowlist rejects path traversal",
             section="SD.defensive", hats=["SD"], criticality="MUST")
def test():
    assert safe_name("a_ok.1") == "a_ok.1"
    for bad in ("../etc", "a/b", "a b", ""):
        try: safe_name(bad)
        except ValueError: continue
        raise AssertionError(f"accepted {bad!r}")

