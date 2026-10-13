"""SIM — simulation. Deterministic stepper."""

from dcs.generate import requirement  # pragma: no cover


def simulate(init, step, n: int):  # pragma: no cover
    s = init
    history = [s]
    for _ in range(n):
        s = step(s)
        history.append(s)
    return history  # pragma: no cover


@requirement(
    id="DCS-SIM-001",
    title="stepper produces n+1 states",
    section="SIM.simulation",
    hats=["SIM"],
    criticality="MUST",
)
def test():  # pragma: no cover
    h = simulate(0, lambda s: s + 1, 5)
    assert h == [0, 1, 2, 3, 4, 5]
