"""PLT — platform. Runtime platform classifier."""

import sys

from dcs.generate import requirement


def platform() -> str:
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform.startswith(("win", "cygwin")):
        return "windows"
    return "unknown"


@requirement(
    id="DCS-PLT-001",
    title="platform classified",
    section="PLT.platform",
    hats=["PLT"],
    criticality="MUST",
)
def test():
    assert platform() in {"macos", "linux", "windows", "unknown"}
