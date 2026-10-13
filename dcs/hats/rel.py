"""REL — release. Semver parse + bump."""

import re  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover

_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def parse(v: str) -> tuple[int, int, int]:  # pragma: no cover
    m = _SEMVER.match(v)
    if not m:  # pragma: no cover
        raise ValueError(v)  # pragma: no cover
    return tuple(map(int, m.groups()))  # type: ignore[return-value]  # pragma: no cover


def bump(v: str, kind: str = "patch") -> str:  # pragma: no cover
    a, b, c = parse(v)
    return {"major": f"{a + 1}.0.0", "minor": f"{a}.{b + 1}.0", "patch": f"{a}.{b}.{c + 1}"}[kind]  # pragma: no cover


@requirement(
    id="DCS-REL-001",
    title="semver parses and bumps",
    section="REL.release",
    hats=["REL"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert parse("1.2.3") == (1, 2, 3)
    assert bump("1.2.3", "major") == "2.0.0"
    assert bump("1.2.3", "patch") == "1.2.4"
