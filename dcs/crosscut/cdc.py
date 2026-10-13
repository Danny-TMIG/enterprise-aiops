"""Change data capture: monotonic version stamps."""

from dcs.generate import requirement  # pragma: no cover


class CDC:  # pragma: no cover
    def __init__(self):  # pragma: no cover
        self._v = 0
        self._events = []

    def emit(self, op: str, key: str):  # pragma: no cover
        self._v += 1
        self._events.append((self._v, op, key))
        return self._v  # pragma: no cover

    def since(self, v: int):  # pragma: no cover
        return [e for e in self._events if e[0] > v]  # pragma: no cover


@requirement(
    id="DCS-XC-CDC-001",
    title="version stamps are monotonic",
    section="X.cdc",
    hats=["DE", "DB", "STE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    c = CDC()
    for i in range(5):
        c.emit("put", f"k{i}")
    vs = [v for v, _, _ in c._events]
    assert vs == sorted(vs) and len(set(vs)) == 5
    assert len(c.since(2)) == 3
