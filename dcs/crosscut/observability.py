"""Structured logging + metrics with bounded cardinality."""

from collections import Counter  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


class Metrics:  # pragma: no cover
    def __init__(self, max_series: int = 10_000):  # pragma: no cover
        self.counters: Counter = Counter()
        self.max_series = max_series

    def inc(self, name: str, **labels):  # pragma: no cover
        key = (name, tuple(sorted(labels.items())))
        if len(self.counters) >= self.max_series and key not in self.counters:  # pragma: no cover
            self.counters[("_dropped", ())] += 1
            return
        self.counters[key] += 1

    def value(self, name: str, **labels) -> int:  # pragma: no cover
        return self.counters.get((name, tuple(sorted(labels.items()))), 0)  # pragma: no cover


@requirement(
    id="DCS-XC-OBS-001",
    title="metrics enforce cardinality ceiling",
    section="X.observability",
    hats=["SRE", "SYS"],
    criticality="MUST",
)
def test():  # pragma: no cover
    m = Metrics(max_series=5)
    for i in range(100):
        m.inc("hits", path=f"/p{i}")
    assert m.value("_dropped") > 0
