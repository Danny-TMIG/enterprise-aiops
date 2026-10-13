"""FW — firmware. Binary frame with a fixed-length header."""

import struct  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover

HDR = struct.Struct("<4sHH")  # magic, version, payload length


def frame(payload: bytes) -> bytes:  # pragma: no cover
    return HDR.pack(b"FW01", 1, len(payload)) + payload  # pragma: no cover


def unframe(blob: bytes) -> tuple[bytes, int, bytes]:  # pragma: no cover
    magic, ver, n = HDR.unpack_from(blob, 0)
    return magic, ver, blob[HDR.size : HDR.size + n]  # pragma: no cover


@requirement(
    id="DCS-FW-001",
    title="frame/unframe round-trips",
    section="FW.firmware",
    hats=["FW"],
    criticality="MUST",
)
def test():  # pragma: no cover
    m, v, p = unframe(frame(b"hello"))
    assert (m, v, p) == (b"FW01", 1, b"hello")
