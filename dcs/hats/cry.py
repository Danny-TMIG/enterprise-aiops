"""CRY — crypto. HMAC-SHA256 with constant-time verify."""
import hmac, hashlib
from dcs.generate import requirement

def sign(key: bytes, msg: bytes) -> bytes:
    return hmac.new(key, msg, hashlib.sha256).digest()

def verify(key: bytes, msg: bytes, tag: bytes) -> bool:
    return hmac.compare_digest(sign(key, msg), tag)

@requirement(id="DCS-CRY-001", title="HMAC verifies and rejects tampered tags",
             section="CRY.crypto", hats=["CRY"], criticality="MUST")
def test():
    k, m = b"k"*32, b"payload"
    t = sign(k, m)
    assert verify(k, m, t)
    assert not verify(k, m + b"!", t)

