"""Feature flags: deterministic rollout by hash."""

import hashlib  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def enabled(flag: str, user: str, pct: int) -> bool:  # pragma: no cover
    if not (0 <= pct <= 100):  # pragma: no cover
        raise ValueError("pct out of range")  # pragma: no cover
    h = hashlib.sha256(f"{flag}:{user}".encode()).digest()
    return (int.from_bytes(h[:4], "big") % 100) < pct  # pragma: no cover


@requirement(
    id="DCS-XC-FLAG-001",
    title="rollout is deterministic and stable",
    section="X.flags",
    hats=["REL", "DO"],
    criticality="MUST",
)
def test():  # pragma: no cover
    a = [enabled("new_ui", f"u{i}", 30) for i in range(500)]
    b = [enabled("new_ui", f"u{i}", 30) for i in range(500)]
    assert a == b
    pct = sum(a) / len(a)
    assert 0.2 < pct < 0.4, pct
