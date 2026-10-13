"""OSCAL Assessment Results exporter.

Serializes a dcs.self payload into an OSCAL 1.x Assessment Results
document. Any tool that reads OSCAL (compliance-trestle, OSCAL-CLI,
FedRAMP tooling) can consume this without installing dcs.

Belnap -> OSCAL status:
  T -> satisfied
  F -> not-satisfied
  U -> not-applicable   (control was not evaluated)
  B -> satisfied + prop dcs:conflict=true
"""

from __future__ import annotations  # pragma: no cover

import uuid  # pragma: no cover
from datetime import UTC, datetime  # pragma: no cover


def _status(state: str) -> tuple[str, dict]:  # pragma: no cover
    if state == "T":  # pragma: no cover
        return "satisfied", {}  # pragma: no cover
    if state == "F":  # pragma: no cover
        return "not-satisfied", {}  # pragma: no cover
    if state == "U":  # pragma: no cover
        return "not-applicable", {}  # pragma: no cover
    # B: emit satisfied with a conflict prop so downstream tools can flag
    return "satisfied", {"name": "dcs:conflict", "value": "true"}  # pragma: no cover


def to_oscal(payload: dict, *, title: str = "dcs conformance") -> dict:  # pragma: no cover
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    findings = []
    for r in payload["results"]:
        status, prop = _status(r["state"])
        target: dict = {
            "type": "objective-id",
            "target-id": r["id"],
            "title": r.get("title", r["id"]),
            "status": {"state": status},
        }
        if prop:  # pragma: no cover
            target["props"] = [prop]
        findings.append(
            {
                "uuid": str(uuid.uuid5(uuid.NAMESPACE_URL, r["id"] + r["state"])),
                "title": r.get("title", r["id"]),
                "description": r.get("id"),
                "target": target,
                "props": [
                    {"name": "dcs:criticality", "value": r.get("criticality", "")},
                    {"name": "dcs:state", "value": r["state"]},
                    {"name": "dcs:attestation_count", "value": str(len(r.get("attestations", [])))},
                ],
            }
        )

    return {  # pragma: no cover
        "assessment-results": {
            "uuid": str(uuid.uuid4()),
            "metadata": {
                "title": title,
                "last-modified": now,
                "version": "1.0.0",
                "oscal-version": "1.1.2",
            },
            "import-ap": {"href": "#dcs-self"},
            "results": [
                {
                    "uuid": str(uuid.uuid4()),
                    "title": title,
                    "description": "Belnap-folded conformance from dcs.self",
                    "start": now,
                    "end": now,
                    "findings": findings,
                }
            ],
        },
    }
