"""Backup / restore round-trip."""

import hashlib  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def snapshot(data: bytes) -> dict:  # pragma: no cover
    return {"bytes": data, "sha256": hashlib.sha256(data).hexdigest()}  # pragma: no cover


def restore(snap: dict) -> bytes:  # pragma: no cover
    assert hashlib.sha256(snap["bytes"]).hexdigest() == snap["sha256"]
    return snap["bytes"]  # pragma: no cover


@requirement(
    id="DCS-XC-BACKUP-001",
    title="snapshot/restore is integrity-checked",
    section="X.backup",
    hats=["STE", "SRE", "SD"],
    criticality="MUST",
)
def test():  # pragma: no cover
    blob = b"critical" * 1000
    s = snapshot(blob)
    assert restore(s) == blob
    s["bytes"] = b"tampered" + s["bytes"]
    try:
        restore(s)
    except AssertionError:  # pragma: no cover
        return
    raise AssertionError("tampered snapshot accepted")  # pragma: no cover
