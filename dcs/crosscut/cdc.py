"""Change data capture: monotonic version stamps."""

from dcs.generate import requirement


class CDC:
    def __init__(self):
        self._v = 0
        self._events = []

    def emit(self, op: str, key: str):
        self._v += 1
        self._events.append((self._v, op, key))
        return self._v

    def since(self, v: int):
        return [e for e in self._events if e[0] > v]


@requirement(
    id="DCS-XC-CDC-001",
    title="version stamps are monotonic",
    section="X.cdc",
    hats=["DE", "DB", "STE"],
    criticality="MUST",
)
def test():
    c = CDC()
    for i in range(5):
        c.emit("put", f"k{i}")
    vs = [v for v, _, _ in c._events]
    assert vs == sorted(vs) and len(set(vs)) == 5
    assert len(c.since(2)) == 3
