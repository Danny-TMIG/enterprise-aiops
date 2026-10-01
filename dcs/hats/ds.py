"""DS — data science. Point estimate + 95% CI."""

import math

from dcs.generate import requirement


def mean(xs):
    return sum(xs) / len(xs)


def var(xs):
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def ci95(xs):
    m = mean(xs)
    s = math.sqrt(var(xs) / len(xs))
    return m - 1.96 * s, m + 1.96 * s


@requirement(
    id="DCS-DS-001",
    title="CI brackets the sample mean",
    section="DS.datascience",
    hats=["DS"],
    criticality="MUST",
)
def test():
    xs = [0.9, 1.0, 1.05, 0.95, 1.02, 0.98]
    lo, hi = ci95(xs)
    assert lo <= mean(xs) <= hi
