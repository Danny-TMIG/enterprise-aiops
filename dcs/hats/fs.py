"""FS — fullstack. A single vertical slice from HTML to JSON."""

from dcs.generate import requirement
from dcs.hats.be import health
from dcs.hats.fe import render_index


def slice_render() -> str:
    """Compose FE markup with a JSON payload fetched from BE."""
    import json

    payload = json.dumps(health().to_dict())
    return render_index() + f"<script>window.__bootstrap__={payload};</script>"


@requirement(
    id="DCS-FS-001",
    title="FE + BE compose into one page",
    section="FS.fullstack",
    hats=["FS"],
    criticality="MUST",
)
def test():
    page = slice_render()
    assert "<h1>" in page and "__bootstrap__" in page
    assert '"status": "ok"' in page or '"status":"ok"' in page
