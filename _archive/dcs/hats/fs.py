"""FS — fullstack. A single vertical slice from HTML to JSON."""

from dcs.generate import requirement  # pragma: no cover
from dcs.hats.be import health  # pragma: no cover
from dcs.hats.fe import render_index  # pragma: no cover


def slice_render() -> str:  # pragma: no cover
    """Compose FE markup with a JSON payload fetched from BE."""
    import json  # pragma: no cover

    payload = json.dumps(health().to_dict())
    return render_index() + f"<script>window.__bootstrap__={payload};</script>"  # pragma: no cover


@requirement(
    id="DCS-FS-001",
    title="FE + BE compose into one page",
    section="FS.fullstack",
    hats=["FS"],
    criticality="MUST",
)
def test():  # pragma: no cover
    page = slice_render()
    assert "<h1>" in page and "__bootstrap__" in page
    assert '"status": "ok"' in page or '"status":"ok"' in page
