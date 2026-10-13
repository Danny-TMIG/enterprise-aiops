"""KRN — kernel. POSIX resource limits, read-only observation."""

import resource  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def limits() -> dict:  # pragma: no cover
    return {  # pragma: no cover
        "nofile": resource.getrlimit(resource.RLIMIT_NOFILE),
        "nproc": resource.getrlimit(resource.RLIMIT_NPROC),
    }


def within_soft(cap: int) -> bool:  # pragma: no cover
    soft, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
    return 0 < soft <= cap  # pragma: no cover


@requirement(
    id="DCS-KRN-001",
    title="process has non-zero soft nofile limit",
    section="KRN.kernel",
    hats=["KRN"],
    criticality="MUST",
)
def test():  # pragma: no cover
    l = limits()
    assert l["nofile"][0] > 0
