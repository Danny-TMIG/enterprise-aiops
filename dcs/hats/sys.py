"""SYS — systems. File descriptor budget accounting."""

import os

from dcs.generate import requirement


def open_fds() -> int:
    try:
        return len(os.listdir("/dev/fd"))
    except FileNotFoundError:
        return len(os.listdir("/proc/self/fd"))


@requirement(
    id="DCS-SYS-001",
    title="open fd count is bounded",
    section="SYS.systems",
    hats=["SYS"],
    criticality="MUST",
)
def test():
    n = open_fds()
    assert 0 < n < 4096, n
