"""SCI — scientific. Kahan summation beats naive for long inputs."""

from dcs.generate import requirement  # pragma: no cover


def kahan(xs) -> float:  # pragma: no cover
    s = 0.0
    c = 0.0
    for x in xs:
        y = x - c
        t = s + y
        c = (t - s) - y
        s = t
    return s  # pragma: no cover


def naive(xs) -> float:  # pragma: no cover
    s = 0.0
    for x in xs:
        s += x
    return s  # pragma: no cover


@requirement(
    id="DCS-SCI-001",
    title="Kahan error below 1e-6 for 10k floats",
    section="SCI.scientific",
    hats=["SCI"],
    criticality="MUST",
)
def test():  # pragma: no cover
    xs = [0.1] * 10_000
    assert abs(kahan(xs) - 1000.0) < 1e-6
