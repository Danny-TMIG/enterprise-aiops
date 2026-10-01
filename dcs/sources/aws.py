"""AWS source — attestations from AWS APIs via boto3.

boto3 is optional. If it isn't installed, or credentials aren't
configured, every source returns U (unknown). The engine folds U as
identity, so a missing AWS connector does not flip the verdict — it
just narrows the evidence base.
"""
from __future__ import annotations

from dcs.sources import Attestation, B, meet, source

try:
    import boto3  # type: ignore[import-not-found]
except ImportError:
    boto3 = None  # type: ignore[assignment]


def _client(service: str):
    if boto3 is None:
        return None
    try:
        return boto3.client(service)
    except Exception:
        return None


def _unavailable(req_id: str) -> Attestation:
    return Attestation(
        req_id, B.U, "aws",
        "boto3 not installed or AWS credentials not configured",
    )


@source("DCS-XC-BACKUP-001")
def s3_encryption_at_rest() -> Attestation:
    """Every S3 bucket must have default encryption configured."""
    c = _client("s3")
    if c is None:
        return _unavailable("DCS-XC-BACKUP-001")
    try:
        buckets = c.list_buckets().get("Buckets", [])
    except Exception as e:
        return Attestation("DCS-XC-BACKUP-001", B.U, "aws",
                           f"list_buckets: {type(e).__name__}: {e}")
    if not buckets:
        return Attestation("DCS-XC-BACKUP-001", B.U, "aws",
                           "no buckets in account")

    states: list[B] = []
    unencrypted: list[str] = []
    unknown: list[str] = []
    for b in buckets:
        name = b["Name"]
        try:
            c.get_bucket_encryption(Bucket=name)
            states.append(B.T)
        except c.exceptions.ClientError as e:
            code = e.response.get("Error", {}).get("Code", "")
            if code == "ServerSideEncryptionConfigurationNotFoundError":
                states.append(B.F)
                unencrypted.append(name)
            else:
                states.append(B.U)
                unknown.append(name)
        except Exception:
            states.append(B.U)
            unknown.append(name)

    folded = states[0]
    for s in states[1:]:
        folded = meet(folded, s)

    enc = len(buckets) - len(unencrypted) - len(unknown)
    reason = f"{enc}/{len(buckets)} buckets encrypted"
    if unencrypted:
        reason += f"; unencrypted: {unencrypted[:3]}"
    if unknown:
        reason += f"; unchecked: {unknown[:3]}"

    return Attestation(
        "DCS-XC-BACKUP-001", folded, "aws", reason,
        {"total": len(buckets), "unencrypted": unencrypted, "unknown": unknown},
    )


@source("DCS-NWE-001")
def cloudtrail_multi_region() -> Attestation:
    """A multi-region CloudTrail trail must be actively logging."""
    c = _client("cloudtrail")
    if c is None:
        return _unavailable("DCS-NWE-001")
    try:
        trails = c.describe_trails(includeShadowTrails=False).get("trailList", [])
    except Exception as e:
        return Attestation("DCS-NWE-001", B.U, "aws",
                           f"describe_trails: {type(e).__name__}: {e}")

    multi = [t for t in trails if t.get("IsMultiRegionTrail")]
    if not multi:
        return Attestation("DCS-NWE-001", B.F, "aws",
                           "no multi-region trail configured",
                           {"trails": [t.get("Name") for t in trails]})

    name = multi[0]["Name"]
    try:
        status = c.get_trail_status(Name=name)
    except Exception as e:
        return Attestation("DCS-NWE-001", B.U, "aws",
                           f"get_trail_status({name}): {type(e).__name__}: {e}")

    logging_on = bool(status.get("IsLogging"))
    state = B.T if logging_on else B.F
    return Attestation(
        "DCS-NWE-001", state, "aws",
        f"trail {name}: multi-region=True, logging={logging_on}",
        {"trail": name, "logging": logging_on},
    )


@source("DCS-XC-PRIV-001")
def iam_password_policy() -> Attestation:
    """Account password policy must meet six baseline checks.

    Partial compliance folds to B (CONFLICT), not F: some checks
    pass, some fail, and that is a two-source disagreement.
    """
    c = _client("iam")
    if c is None:
        return _unavailable("DCS-XC-PRIV-001")
    try:
        p = c.get_account_password_policy()["PasswordPolicy"]
    except c.exceptions.NoSuchEntityException:
        return Attestation("DCS-XC-PRIV-001", B.F, "aws",
                           "no account password policy")
    except Exception as e:
        return Attestation("DCS-XC-PRIV-001", B.U, "aws",
                           f"get_account_password_policy: {type(e).__name__}: {e}")

    checks = {
        "min_length_14": p.get("MinimumPasswordLength", 0) >= 14,
        "requires_symbols": bool(p.get("RequireSymbols")),
        "requires_numbers": bool(p.get("RequireNumbers")),
        "requires_upper": bool(p.get("RequireUppercaseCharacters")),
        "requires_lower": bool(p.get("RequireLowercaseCharacters")),
        "max_age_90": 0 < p.get("MaxPasswordAge", 999) <= 90,
    }
    passed = sum(checks.values())
    total = len(checks)
    if passed == total:
        state = B.T
    elif passed == 0:
        state = B.F
    else:
        state = B.B

    return Attestation(
        "DCS-XC-PRIV-001", state, "aws",
        f"{passed}/{total} password-policy checks pass",
        {"checks": checks, "policy": p},
    )
