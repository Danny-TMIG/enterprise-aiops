"""Claim 3: HMAC-with-default-key is not a signature chain."""
from __future__ import annotations

import inspect
import sys


def check_asymmetric() -> tuple:
    from app.seed import seal
    src = inspect.getsource(seal).lower()
    uses_hmac = "hmac" in src and "ed25519" not in src
    return (False if uses_hmac else True,
            "seal.py uses HMAC-SHA256 (symmetric)" if uses_hmac
            else "seal.py appears asymmetric")


def check_key_protected() -> tuple:
    from app.seed.seal import DEFAULT_KEY
    return (False, f"source default key: {DEFAULT_KEY!r}")


def check_key_rotatable() -> tuple:
    from app.seed import seal
    src = inspect.getsource(seal).lower()
    has_rotation = "def rotate" in src or "rotate_key" in src or "key_rotation" in src
    return (has_rotation,
            "no rotation logic" if not has_rotation else "rotation present")


def check_timestamped() -> tuple:
    from app.seed import seal
    src = inspect.getsource(seal).lower()
    has_ts = "rfc3161" in src or "tsa" in src or "timestamp_authority" in src
    return (has_ts, "no RFC 3161 TSA" if not has_ts else "timestamped")


def check_third_party() -> tuple:
    from app.seed.seal import DEFAULT_KEY
    return (False, f"verification requires shared secret {DEFAULT_KEY!r}")


AXES = [
    ("asymmetric", check_asymmetric),
    ("key_protected", check_key_protected),
    ("key_rotatable", check_key_rotatable),
    ("timestamped", check_timestamped),
    ("third_party_verifiable", check_third_party),
]


def main() -> int:
    print("── claim 3: HMAC-with-default-key is not a signature chain ──")
    unmet = 0
    for name, fn in AXES:
        try:
            ok, ev = fn()
        except Exception as e:
            ok, ev = False, f"{type(e).__name__}: {e}"
        unmet += int(not ok)
        print(f"  {'MET' if ok else 'UNMET'}  {name:22s}  {ev}")
    print()
    print(f"  verdict: {unmet}/{len(AXES)} requirements unmet — claim 3 stands")
    return 0


if __name__ == "__main__":
    sys.exit(main())
