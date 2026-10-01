"""Structured logging + metrics with bounded cardinality."""
from collections import Counter
from dcs.generate import requirement

class Metrics:
    def __init__(self, max_series: int = 10_000):
        self.counters: Counter = Counter()
        self.max_series = max_series
    def inc(self, name: str, **labels):
        key = (name, tuple(sorted(labels.items())))
        if len(self.counters) >= self.max_series and key not in self.counters:
            self.counters[("_dropped", ())] += 1
            return
        self.counters[key] += 1
    def value(self, name: str, **labels) -> int:
        return self.counters.get((name, tuple(sorted(labels.items()))), 0)

@requirement(id="DCS-XC-OBS-001", title="metrics enforce cardinality ceiling",
             section="X.observability", hats=["SRE", "SYS"], criticality="MUST")
def test():
    m = Metrics(max_series=5)
    for i in range(100):
        m.inc("hits", path=f"/p{i}")
    assert m.value("_dropped") > 0
