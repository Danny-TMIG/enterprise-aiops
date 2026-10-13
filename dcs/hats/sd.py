"""SD — sec defensive. Input allowlist."""

import re  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover

OK = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")


def safe_name(s: str) -> str:  # pragma: no cover
    if not OK.fullmatch(s):  # pragma: no cover
        raise ValueError(f"unsafe name: {s!r}")  # pragma: no cover
    return s  # pragma: no cover


@requirement(
    id="DCS-SD-001",
    title="allowlist rejects path traversal",
    section="SD.defensive",
    hats=["SD"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert safe_name("a_ok.1") == "a_ok.1"
    for bad in ("../etc", "a/b", "a b", ""):
        try:
            safe_name(bad)
        except ValueError:  # pragma: no cover
            continue
        raise AssertionError(f"accepted {bad!r}")  # pragma: no cover
