"""CMP-DAT-001 — data staging and result collection.

Content-addressed staging area. Every staged artifact is written to a
hash-named path and recorded in a manifest. Result collection reads back
by manifest id and verifies the hash before returning.
"""
from __future__ import annotations
import hashlib
import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class StagingError(RuntimeError):
    pass


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@dataclass
class StagedArtifact:
    artifact_id: str
    content_hash: str
    size_bytes: int
    staged_at: float
    origin: str
    tags: dict[str, str] = field(default_factory=dict)


class StagingArea:
    def __init__(self, root: Optional[Path] = None) -> None:
        self._root = Path(root) if root else Path(tempfile.mkdtemp(prefix="asf-stage-"))
        self._blobs = self._root / "blobs"
        self._blobs.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self._root / "manifest.jsonl"
        self._index: dict[str, StagedArtifact] = {}
        if self._manifest_path.exists():
            for line in self._manifest_path.read_text().splitlines():
                d = json.loads(line)
                a = StagedArtifact(**d)
                self._index[a.artifact_id] = a

    def stage(self, data: bytes, *, origin: str, tags: Optional[dict[str, str]] = None) -> StagedArtifact:
        if not isinstance(data, (bytes, bytearray)):
            raise StagingError("data must be bytes")
        content_hash = _sha256(bytes(data))
        artifact_id = f"a-{content_hash[:16]}"
        blob_path = self._blobs / content_hash
        if not blob_path.exists():
            tmp = blob_path.with_suffix(".tmp")
            tmp.write_bytes(bytes(data))
            os.replace(tmp, blob_path)
        artifact = StagedArtifact(
            artifact_id=artifact_id,
            content_hash=content_hash,
            size_bytes=len(data),
            staged_at=time.time(),
            origin=origin,
            tags=dict(tags or {}),
        )
        self._index[artifact_id] = artifact
        with self._manifest_path.open("a") as f:
            f.write(json.dumps(artifact.__dict__) + "\n")
        return artifact

    def collect(self, artifact_id: str) -> bytes:
        a = self._index.get(artifact_id)
        if not a:
            raise StagingError(f"unknown artifact {artifact_id}")
        blob = (self._blobs / a.content_hash).read_bytes()
        if _sha256(blob) != a.content_hash:
            raise StagingError(f"hash mismatch for {artifact_id}")
        return blob

    def list_ids(self) -> list[str]:
        return sorted(self._index.keys())

    def verify_all(self) -> dict[str, bool]:
        return {
            aid: _sha256((self._blobs / a.content_hash).read_bytes()) == a.content_hash
            for aid, a in self._index.items()
        }
