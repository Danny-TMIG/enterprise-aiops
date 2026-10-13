"""Wall clock vs monotonic — elapsed never goes backwards."""

import time  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


@requirement(
    id="DCS-XC-TIME-001",
    title="elapsed monotonic time is non-negative",
    section="X.time",
    hats=["SYS", "SIM"],
    criticality="MUST",
)
def test():  # pragma: no cover
    t0 = time.monotonic()
    time.sleep(0.001)
    t1 = time.monotonic()
    assert t1 >= t0
