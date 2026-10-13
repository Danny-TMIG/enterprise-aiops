"""STE — storage eng. Append-only segment store."""

from dcs.generate import requirement  # pragma: no cover


class Segment:  # pragma: no cover
    def __init__(self):  # pragma: no cover
        self._chunks: list[bytes] = []

    def append(self, b: bytes) -> int:  # pragma: no cover
        self._chunks.append(b)
        return len(self._chunks) - 1  # pragma: no cover

    def read(self, i: int) -> bytes:  # pragma: no cover
        return self._chunks[i]  # pragma: no cover

    def size(self) -> int:  # pragma: no cover
        return len(self._chunks)  # pragma: no cover


@requirement(
    id="DCS-STE-001",
    title="segment appends are indexed and readable",
    section="STE.storage",
    hats=["STE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    s = Segment()
    assert s.append(b"a") == 0
    assert s.append(b"b") == 1
    assert s.read(1) == b"b"
    assert s.size() == 2
