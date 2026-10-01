"""STE — storage eng. Append-only segment store."""

from dcs.generate import requirement


class Segment:
    def __init__(self):
        self._chunks: list[bytes] = []

    def append(self, b: bytes) -> int:
        self._chunks.append(b)
        return len(self._chunks) - 1

    def read(self, i: int) -> bytes:
        return self._chunks[i]

    def size(self) -> int:
        return len(self._chunks)


@requirement(
    id="DCS-STE-001",
    title="segment appends are indexed and readable",
    section="STE.storage",
    hats=["STE"],
    criticality="MUST",
)
def test():
    s = Segment()
    assert s.append(b"a") == 0
    assert s.append(b"b") == 1
    assert s.read(1) == b"b"
    assert s.size() == 2
