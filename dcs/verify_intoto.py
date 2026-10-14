"""In-toto style attestations.

A Statement binds a subject (artifacts with digests) to a predicate
(a claim about how the artifacts were produced). An Envelope wraps a
Statement with a signature. verify_envelope checks the signature
against the signer's key.

Shape follows the in-toto attestation spec v0.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .verify import HMACVerifier, canonical, digest_of

STATEMENT_TYPE = "https://in-toto.io/Statement/v0.1"
PAYLOAD_TYPE = "application/vnd.in-toto+json"


@dataclass(frozen=True)
class Subject:
    name: str
    digest: dict[str, str]

    @classmethod
    def of(cls, name: str, content: bytes | str) -> Subject:
        return cls(name=name, digest={"sha256": digest_of(content)})


@dataclass(frozen=True)
class Statement:
    subject: list[Subject]
    predicate_type: str
    predicate: dict[str, Any]

    def to_json(self) -> dict[str, Any]:
        return {
            "_type": STATEMENT_TYPE,
            "subject": [{"name": s.name, "digest": dict(s.digest)} for s in self.subject],
            "predicateType": self.predicate_type,
            "predicate": self.predicate,
        }


@dataclass(frozen=True)
class Envelope:
    statement: dict[str, Any]
    signature: str

    def to_json(self) -> dict[str, Any]:
        return {
            "payloadType": PAYLOAD_TYPE,
            "payload": self.statement,
            "signatures": [{"sig": self.signature}],
        }


def sign_statement(statement: Statement, signer: HMACVerifier) -> Envelope:
    payload = canonical(statement.to_json())
    sig_hex = signer.sign(payload).hex()
    return Envelope(statement=statement.to_json(), signature=sig_hex)


def verify_envelope(envelope: Envelope, verifier: HMACVerifier) -> bool:
    payload = canonical(envelope.statement)
    try:
        sig = bytes.fromhex(envelope.signature)
    except ValueError:
        return False
    return verifier.verify(payload, sig)
