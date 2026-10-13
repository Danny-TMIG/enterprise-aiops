"""MLE — ml eng. Model artifact manifest with checksum."""

from dcs.generate import requirement  # pragma: no cover


def manifest(model_id: str, sha: str, metrics: dict) -> dict:  # pragma: no cover
    return {"model_id": model_id, "sha256": sha, "metrics": metrics, "schema": 1}  # pragma: no cover


def validate(m: dict) -> None:  # pragma: no cover
    if m.get("schema") != 1:  # pragma: no cover
        raise ValueError("bad schema")  # pragma: no cover
    if not m.get("sha256", "").startswith("sha256:"):  # pragma: no cover
        raise ValueError("bad sha")  # pragma: no cover


@requirement(
    id="DCS-MLE-001",
    title="manifest schema is enforced",
    section="MLE.mleng",
    hats=["MLE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    m = manifest("rubik-q", "sha256:abc", {"top1": 0.9})
    validate(m)
    try:
        validate({**m, "schema": 2})
    except ValueError:  # pragma: no cover
        return
    raise AssertionError("bad schema not rejected")  # pragma: no cover
