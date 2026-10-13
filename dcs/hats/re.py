"""RE — reverse eng. Round-trip an opaque binary format."""

import struct  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def encode(rows: list[tuple[int, int]]) -> bytes:  # pragma: no cover
    return b"".join(struct.pack("<II", a, b) for a, b in rows)  # pragma: no cover


def decode(blob: bytes) -> list[tuple[int, int]]:  # pragma: no cover
    if len(blob) % 8:  # pragma: no cover
        raise ValueError("truncated")  # pragma: no cover
    return [struct.unpack_from("<II", blob, i * 8) for i in range(len(blob) // 8)]  # pragma: no cover


@requirement(
    id="DCS-RE-001",
    title="opaque blob round-trips",
    section="RE.reverse",
    hats=["RE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    rows = [(1, 2), (3, 4), (0xFFFF, 0)]
    assert decode(encode(rows)) == rows
    try:
        decode(b"abc")
    except ValueError:  # pragma: no cover
        return
    raise AssertionError("truncated blob accepted")  # pragma: no cover
