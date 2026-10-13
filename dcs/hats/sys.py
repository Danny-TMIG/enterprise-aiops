"""SYS — systems. File descriptor budget accounting."""

import os  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def open_fds() -> int:  # pragma: no cover
    try:
        return len(os.listdir("/dev/fd"))  # pragma: no cover
    except FileNotFoundError:  # pragma: no cover
        return len(os.listdir("/proc/self/fd"))  # pragma: no cover


@requirement(
    id="DCS-SYS-001",
    title="open fd count is bounded",
    section="SYS.systems",
    hats=["SYS"],
    criticality="MUST",
)
def test():  # pragma: no cover
    n = open_fds()
    assert 0 < n < 4096, n
