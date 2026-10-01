"""SCI — scientific. Kahan summation beats naive for long inputs."""

from dcs.generate import requirement


def kahan(xs) -> float:
    s = 0.0
    c = 0.0
    for x in xs:
        y = x - c
        t = s + y
        c = (t - s) - y
        s = t
    return s


def naive(xs) -> float:
    s = 0.0
    for x in xs:
        s += x
    return s


@requirement(
    id="DCS-SCI-001",
    title="Kahan error below 1e-6 for 10k floats",
    section="SCI.scientific",
    hats=["SCI"],
    criticality="MUST",
)
def test():
    xs = [0.1] * 10_000
    assert abs(kahan(xs) - 1000.0) < 1e-6
