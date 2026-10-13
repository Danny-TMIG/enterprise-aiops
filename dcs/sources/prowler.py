"""Prowler source — Prowler v5 JSON-OCSF output.

Prowler emits one finding per (check, resource). We fold them per
requirement id if the check name maps, otherwise aggregate under a
single synthetic requirement.
"""

from __future__ import annotations  # pragma: no cover

from dcs.sources import Attestation, B, meet, source  # pragma: no cover
from dcs.sources._file import read_json  # pragma: no cover

# Prowler check name -> dcs requirement id. Extend as you onboard.
CHECK_MAP: dict[str, str] = {
    "s3_bucket_default_encryption": "DCS-XC-BACKUP-001",
    "cloudtrail_multi_region_enabled": "DCS-NWE-001",
    "iam_password_policy_minimum_length_14": "DCS-XC-PRIV-001",
}


def _ocsf_state(finding: dict) -> B:  # pragma: no cover
    """OCSF findings carry status_code; COMPLIANT vs FAIL vs everything else."""
    status = str(finding.get("status_code", "")).upper()
    if status in ("PASS", "COMPLIANT", "SUCCESS"):  # pragma: no cover
        return B.T  # pragma: no cover
    if status in ("FAIL", "FAILED", "NON_COMPLIANT"):  # pragma: no cover
        return B.F  # pragma: no cover
    return B.U  # pragma: no cover


@source("DCS-XC-BACKUP-001")
def prowler_findings() -> Attestation:  # pragma: no cover
    return _aggregate("DCS-XC-BACKUP-001")  # pragma: no cover


@source("DCS-NWE-001")
def prowler_network_findings() -> Attestation:  # pragma: no cover
    return _aggregate("DCS-NWE-001")  # pragma: no cover


@source("DCS-XC-PRIV-001")
def prowler_privacy_findings() -> Attestation:  # pragma: no cover
    return _aggregate("DCS-XC-PRIV-001")  # pragma: no cover


def _aggregate(req_id: str) -> Attestation:  # pragma: no cover
    data, err = read_json("DCS_PROWLER_JSON", req_id, "prowler")
    if err:  # pragma: no cover
        return err  # pragma: no cover
    if data is None:  # pragma: no cover
        return Attestation(req_id, B.U, "prowler", "no data")  # pragma: no cover
    findings = data if isinstance(data, list) else data.get("findings", [])
    if not findings:  # pragma: no cover
        return Attestation(req_id, B.U, "prowler", "no findings")  # pragma: no cover

    matching = [
        f for f in findings if CHECK_MAP.get(f.get("check_id", ""), f.get("check_id", "")) == req_id
    ]
    if not matching:  # pragma: no cover
        return Attestation(req_id, B.U, "prowler", f"no findings mapped to {req_id}")  # pragma: no cover

    states = [_ocsf_state(f) for f in matching]
    folded = states[0]
    for s in states[1:]:
        folded = meet(folded, s)
    fails = [f.get("resource_uid", "?") for f, s in zip(matching, states) if s == B.F]
    return Attestation(  # pragma: no cover
        req_id,
        folded,
        "prowler",
        f"{len(matching)} findings, {len(fails)} fail",
        {"failures": fails[:10]},
    )
