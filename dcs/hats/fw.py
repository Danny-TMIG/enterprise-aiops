"""FW — firmware. Binary frame with a fixed-length header."""
import struct
from dcs.generate import requirement

HDR = struct.Struct("<4sHH")   # magic, version, payload length

def frame(payload: bytes) -> bytes:
    return HDR.pack(b"FW01", 1, len(payload)) + payload

def unframe(blob: bytes) -> tuple[bytes, int, bytes]:
    magic, ver, n = HDR.unpack_from(blob, 0)
    return magic, ver, blob[HDR.size:HDR.size+n]

@requirement(id="DCS-FW-001", title="frame/unframe round-trips",
             section="FW.firmware", hats=["FW"], criticality="MUST")
def test():
    m, v, p = unframe(frame(b"hello"))
    assert (m, v, p) == (b"FW01", 1, b"hello")

