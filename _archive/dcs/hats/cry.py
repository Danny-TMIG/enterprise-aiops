"""CRY — crypto. HMAC-SHA256 with constant-time verify."""

import hashlib  # pragma: no cover
import hmac  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def sign(key: bytes, msg: bytes) -> bytes:  # pragma: no cover
    return hmac.new(key, msg, hashlib.sha256).digest()  # pragma: no cover


def verify(key: bytes, msg: bytes, tag: bytes) -> bool:  # pragma: no cover
    return hmac.compare_digest(sign(key, msg), tag)  # pragma: no cover


@requirement(
    id="DCS-CRY-001",
    title="HMAC verifies and rejects tampered tags",
    section="CRY.crypto",
    hats=["CRY"],
    criticality="MUST",
)
def test():  # pragma: no cover
    k, m = b"k" * 32, b"payload"
    t = sign(k, m)
    assert verify(k, m, t)
    assert not verify(k, m + b"!", t)
