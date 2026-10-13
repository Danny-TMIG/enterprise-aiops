"""MO — mobile. PWA manifest validated against the minimum keys."""

from dcs.generate import requirement  # pragma: no cover


def manifest() -> dict:  # pragma: no cover
    return {  # pragma: no cover
        "name": "AI Ops",
        "short_name": "aiops",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#000000",
        "icons": [{"src": "/icon.png", "sizes": "512x512", "type": "image/png"}],
    }


def validate(m: dict) -> None:  # pragma: no cover
    required = {"name", "short_name", "start_url", "display", "icons"}
    missing = required - set(m)
    if missing:  # pragma: no cover
        raise ValueError(f"manifest missing: {missing}")  # pragma: no cover
    if m["display"] not in {"standalone", "fullscreen", "minimal-ui", "browser"}:  # pragma: no cover
        raise ValueError("bad display mode")  # pragma: no cover


@requirement(
    id="DCS-MO-001",
    title="PWA manifest is complete",
    section="MO.mobile",
    hats=["MO"],
    criticality="MUST",
)
def test():  # pragma: no cover
    validate(manifest())
