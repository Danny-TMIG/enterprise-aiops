"""MLE — ml eng. Model artifact manifest with checksum."""

from dcs.generate import requirement


def manifest(model_id: str, sha: str, metrics: dict) -> dict:
    return {"model_id": model_id, "sha256": sha, "metrics": metrics, "schema": 1}


def validate(m: dict) -> None:
    if m.get("schema") != 1:
        raise ValueError("bad schema")
    if not m.get("sha256", "").startswith("sha256:"):
        raise ValueError("bad sha")


@requirement(
    id="DCS-MLE-001",
    title="manifest schema is enforced",
    section="MLE.mleng",
    hats=["MLE"],
    criticality="MUST",
)
def test():
    m = manifest("rubik-q", "sha256:abc", {"top1": 0.9})
    validate(m)
    try:
        validate({**m, "schema": 2})
    except ValueError:
        return
    raise AssertionError("bad schema not rejected")
