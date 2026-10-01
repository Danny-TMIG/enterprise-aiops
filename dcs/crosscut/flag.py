"""Feature flags: deterministic rollout by hash."""
import hashlib
from dcs.generate import requirement

def enabled(flag: str, user: str, pct: int) -> bool:
    if not (0 <= pct <= 100): raise ValueError("pct out of range")
    h = hashlib.sha256(f"{flag}:{user}".encode()).digest()
    return (int.from_bytes(h[:4], "big") % 100) < pct

@requirement(id="DCS-XC-FLAG-001", title="rollout is deterministic and stable",
             section="X.flags", hats=["REL", "DO"], criticality="MUST")
def test():
    a = [enabled("new_ui", f"u{i}", 30) for i in range(500)]
    b = [enabled("new_ui", f"u{i}", 30) for i in range(500)]
    assert a == b
    pct = sum(a) / len(a)
    assert 0.2 < pct < 0.4, pct
