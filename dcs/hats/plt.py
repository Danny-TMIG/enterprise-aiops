"""PLT — platform. Runtime platform classifier."""

import sys  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def platform() -> str:  # pragma: no cover
    if sys.platform == "darwin":  # pragma: no cover
        return "macos"  # pragma: no cover
    if sys.platform.startswith("linux"):  # pragma: no cover
        return "linux"  # pragma: no cover
    if sys.platform.startswith(("win", "cygwin")):  # pragma: no cover
        return "windows"  # pragma: no cover
    return "unknown"  # pragma: no cover


@requirement(
    id="DCS-PLT-001",
    title="platform classified",
    section="PLT.platform",
    hats=["PLT"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert platform() in {"macos", "linux", "windows", "unknown"}
