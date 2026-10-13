"""AWS source — attestations from AWS APIs via boto3.

boto3 is optional. If it isn't installed, or credentials aren't
configured, every source returns U (unknown). U is identity in the
Belnap meet, so the verdict narrows but does not break.
"""

from __future__ import annotations  # pragma: no cover

from dcs.sources import Attestation, B, meet, source  # pragma: no cover

try:
    import boto3  # type: ignore[import-not-found]  # pragma: no cover
except ImportError:  # pragma: no cover
    boto3 = None  # type: ignore[assignment]


def _client(service: str):  # pragma: no cover
    if boto3 is None:  # pragma: no cover
        return None  # pragma: no cover
    try:
        return boto3.client(service)  # pragma: no cover
    except Exception:  # pragma: no cover
        return None  # pragma: no cover


def _unavailable(req_id: str) -> Attestation:  # pragma: no cover
    return Attestation(req_id, B.U, "aws", "boto3 not installed or AWS credentials not configured")  # pragma: no cover


@source("DCS-XC-BACKUP-001")
def s3_encryption_at_rest() -> Attestation:  # pragma: no cover
    """Every S3 bucket must have default encryption configured."""
    c = _client("s3")
    if c is None:  # pragma: no cover
        return _unavailable("DCS-XC-BACKUP-001")  # pragma: no cover
    try:
        buckets = c.list_buckets().get("Buckets", [])
    except Exception as e:  # pragma: no cover
        return Attestation(  # pragma: no cover
            "DCS-XC-BACKUP-001", B.U, "aws", f"list_buckets: {type(e).__name__}: {e}"
        )
    if not buckets:  # pragma: no cover
        return Attestation("DCS-XC-BACKUP-001", B.U, "aws", "no buckets")  # pragma: no cover

    states: list[B] = []
    unencrypted: list[str] = []
    unknown: list[str] = []
    for b in buckets:
        name = b["Name"]
        try:
            c.get_bucket_encryption(Bucket=name)
            states.append(B.T)
        except c.exceptions.ClientError as e:  # pragma: no cover
            code = e.response.get("Error", {}).get("Code", "")
            if code == "ServerSideEncryptionConfigurationNotFoundError":  # pragma: no cover
                states.append(B.F)
                unencrypted.append(name)
            else:
                states.append(B.U)
                unknown.append(name)
        except Exception:  # pragma: no cover
            states.append(B.U)
            unknown.append(name)

    folded = states[0]
    for s in states[1:]:
        folded = meet(folded, s)

    enc = len(buckets) - len(unencrypted) - len(unknown)
    reason = f"{enc}/{len(buckets)} buckets encrypted"
    if unencrypted:  # pragma: no cover
        reason += f"; unencrypted: {unencrypted[:3]}"
    if unknown:  # pragma: no cover
        reason += f"; unchecked: {unknown[:3]}"

    return Attestation(  # pragma: no cover
        "DCS-XC-BACKUP-001",
        folded,
        "aws",
        reason,
        {"total": len(buckets), "unencrypted": unencrypted, "unknown": unknown},
    )


@source("DCS-NWE-001")
def cloudtrail_multi_region() -> Attestation:  # pragma: no cover
    """A multi-region CloudTrail trail must be actively logging."""
    c = _client("cloudtrail")
    if c is None:  # pragma: no cover
        return _unavailable("DCS-NWE-001")  # pragma: no cover
    try:
        trails = c.describe_trails(includeShadowTrails=False).get("trailList", [])
    except Exception as e:  # pragma: no cover
        return Attestation("DCS-NWE-001", B.U, "aws", f"describe_trails: {type(e).__name__}: {e}")  # pragma: no cover

    multi = [t for t in trails if t.get("IsMultiRegionTrail")]
    if not multi:  # pragma: no cover
        return Attestation("DCS-NWE-001", B.F, "aws", "no multi-region trail configured")  # pragma: no cover

    name = multi[0]["Name"]
    try:
        status = c.get_trail_status(Name=name)
    except Exception as e:  # pragma: no cover
        return Attestation("DCS-NWE-001", B.U, "aws", f"get_trail_status: {type(e).__name__}: {e}")  # pragma: no cover

    logging_on = bool(status.get("IsLogging"))
    return Attestation(  # pragma: no cover
        "DCS-NWE-001",
        B.T if logging_on else B.F,
        "aws",
        f"trail {name}: multi-region=True, logging={logging_on}",
        {"trail": name, "logging": logging_on},
    )


@source("DCS-XC-PRIV-001")
def iam_password_policy() -> Attestation:  # pragma: no cover
    """Account password policy must meet six baseline checks."""
    c = _client("iam")
    if c is None:  # pragma: no cover
        return _unavailable("DCS-XC-PRIV-001")  # pragma: no cover
    try:
        p = c.get_account_password_policy()["PasswordPolicy"]
    except c.exceptions.NoSuchEntityException:  # pragma: no cover
        return Attestation("DCS-XC-PRIV-001", B.F, "aws", "no policy")  # pragma: no cover
    except Exception as e:  # pragma: no cover
        return Attestation(  # pragma: no cover
            "DCS-XC-PRIV-001", B.U, "aws", f"get_account_password_policy: {type(e).__name__}: {e}"
        )

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
    state = B.T if passed == total else (B.F if passed == 0 else B.B)
    return Attestation(  # pragma: no cover
        "DCS-XC-PRIV-001",
        state,
        "aws",
        f"{passed}/{total} password-policy checks pass",
        {"checks": checks},
    )
