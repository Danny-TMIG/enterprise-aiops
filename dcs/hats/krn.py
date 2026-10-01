"""KRN — kernel. POSIX resource limits, read-only observation."""

import resource

from dcs.generate import requirement


def limits() -> dict:
    return {
        "nofile": resource.getrlimit(resource.RLIMIT_NOFILE),
        "nproc": resource.getrlimit(resource.RLIMIT_NPROC),
    }


def within_soft(cap: int) -> bool:
    soft, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
    return 0 < soft <= cap


@requirement(
    id="DCS-KRN-001",
    title="process has non-zero soft nofile limit",
    section="KRN.kernel",
    hats=["KRN"],
    criticality="MUST",
)
def test():
    l = limits()
    assert l["nofile"][0] > 0
