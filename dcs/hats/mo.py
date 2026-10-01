"""MO — mobile. PWA manifest validated against the minimum keys."""
from dcs.generate import requirement

def manifest() -> dict:
    return {
        "name": "AI Ops",
        "short_name": "aiops",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#000000",
        "icons": [{"src":"/icon.png","sizes":"512x512","type":"image/png"}],
    }

def validate(m: dict) -> None:
    required = {"name","short_name","start_url","display","icons"}
    missing = required - set(m)
    if missing: raise ValueError(f"manifest missing: {missing}")
    if m["display"] not in {"standalone","fullscreen","minimal-ui","browser"}:
        raise ValueError("bad display mode")

@requirement(id="DCS-MO-001", title="PWA manifest is complete",
             section="MO.mobile", hats=["MO"], criticality="MUST")
def test():
    validate(manifest())

