"""Agency, License, Certification, Expertise.

Each primitive is a record anchored to an evidence_hash and to a
provenance chain. None of them is self-asserted. Every one is
revocable. Expertise is not granted — it is accumulated from the
execution history and cannot be forged, only earned.

Field meanings:

  Agency         — the right to act at all, in a scope.
  License        — the right to operate in a specific domain
                   and jurisdiction under stated terms.
  Certification  — a verified claim of conformance to a standard
                   at a version and level.
  Expertise      — the accumulated, evidence-weighted track record
                   of a subject in a domain.
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _h(*parts: str) -> str:
    m = hashlib.sha256()
    for p in parts:
        m.update(p.encode("utf-8"))
        m.update(b"\x1f")
    return "sha256:" + m.hexdigest()


def _revoked(expires_at: str | None) -> bool:
    if not expires_at:
        return False
    return expires_at < _now()


# ── Agency ───────────────────────────────────────────────────────
@dataclass(frozen=True)
class Agency:
    subject: str                    # mesh node id or actor id
    scope: str                      # capability namespace, e.g. "code.write"
    authority: str                  # who holds the underlying authority
    granted_by: str                 # who delegated
    evidence_hash: str              # hash of the grant decision
    issued_at: str = field(default_factory=_now)
    expires_at: str | None = None
    revoked: bool = False

    @property
    def id(self) -> str:
        return _h("agency", self.subject, self.scope,
                  self.authority, self.evidence_hash)

    @property
    def live(self) -> bool:
        return not self.revoked and not _revoked(self.expires_at)


# ── License ──────────────────────────────────────────────────────
@dataclass(frozen=True)
class License:
    subject: str
    domain: str                     # e.g. "k8s.production.eu-west-1"
    jurisdiction: str               # e.g. "org:acme" or "eu"
    terms: str                      # short form of the terms
    issued_by: str
    evidence_hash: str
    issued_at: str = field(default_factory=_now)
    expires_at: str | None = None
    revoked: bool = False

    @property
    def id(self) -> str:
        return _h("license", self.subject, self.domain,
                  self.jurisdiction, self.evidence_hash)

    @property
    def live(self) -> bool:
        return not self.revoked and not _revoked(self.expires_at)


# ── Certification ────────────────────────────────────────────────
@dataclass(frozen=True)
class Certification:
    subject: str
    standard: str                   # e.g. "OWASP-ASVS"
    version: str                    # e.g. "4.0.3"
    level: str                      # e.g. "L2"
    issued_by: str
    evidence_hash: str
    issued_at: str = field(default_factory=_now)
    expires_at: str | None = None
    revoked: bool = False

    @property
    def id(self) -> str:
        return _h("cert", self.subject, self.standard,
                  self.version, self.level, self.evidence_hash)

    @property
    def live(self) -> bool:
        return not self.revoked and not _revoked(self.expires_at)


# ── Expertise (earned, not granted) ──────────────────────────────
@dataclass
class Expertise:
    subject: str
    domain: str
    completions: int = 0
    successes: int = 0
    failures: int = 0
    evidence_hashes: list[str] = field(default_factory=list)
    last_updated: str = field(default_factory=_now)

    def record(self, success: bool, evidence_hash: str) -> None:
        self.completions += 1
        if success:
            self.successes += 1
        else:
            self.failures += 1
        self.evidence_hashes.append(evidence_hash)
        # keep the log bounded but preserve last 64 evidence refs
        self.evidence_hashes = self.evidence_hashes[-64:]
        self.last_updated = _now()

    def score(self) -> float:
        """Wilson lower bound on success rate. 0.0 with no history."""
        n = self.completions
        if n == 0:
            return 0.0
        p = self.successes / n
        z = 1.96
        denom = 1 + z * z / n
        centre = p + z * z / (2 * n)
        margin = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
        return round(max(0.0, (centre - margin) / denom), 4)

    @property
    def id(self) -> str:
        return _h("expertise", self.subject, self.domain)


class AgencyPrimitive:

    """Base record for every governance object the registry tracks.

    A primitive has an identity (name/id), a subject it applies to,
    a lifecycle (issued_at, revoked_at, live), and free-form metadata.
    """
    def __init__(
        self,
        name: str = "",
        id: str | None = None,
        subject: str = "",
        issued_at: str = "",
        revoked_at: str | None = None,
        **metadata,
    ):
        self.name = name
        self.id = id if id is not None else name
        self.subject = subject
        self.issued_at = issued_at
        self.revoked_at = revoked_at
        self.metadata = metadata

    @property
    def live(self) -> bool:
        return self.revoked_at is None

    def revoke(self, when: str = "") -> AgencyPrimitive:
        self.revoked_at = when
        return self

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "id": self.id,
            "subject": self.subject,
            "issued_at": self.issued_at,
            "revoked_at": self.revoked_at,
            "live": self.live,
            "metadata": dict(self.metadata),
        }

    def __repr__(self) -> str:
        return f"AgencyPrimitive({self.name!r}, live={self.live})"

