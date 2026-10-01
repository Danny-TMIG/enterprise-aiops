"""RE — reverse eng. Round-trip an opaque binary format."""

import struct

from dcs.generate import requirement


def encode(rows: list[tuple[int, int]]) -> bytes:
    return b"".join(struct.pack("<II", a, b) for a, b in rows)


def decode(blob: bytes) -> list[tuple[int, int]]:
    if len(blob) % 8:
        raise ValueError("truncated")
    return [struct.unpack_from("<II", blob, i * 8) for i in range(len(blob) // 8)]


@requirement(
    id="DCS-RE-001",
    title="opaque blob round-trips",
    section="RE.reverse",
    hats=["RE"],
    criticality="MUST",
)
def test():
    rows = [(1, 2), (3, 4), (0xFFFF, 0)]
    assert decode(encode(rows)) == rows
    try:
        decode(b"abc")
    except ValueError:
        return
    raise AssertionError("truncated blob accepted")
