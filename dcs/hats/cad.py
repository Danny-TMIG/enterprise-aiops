"""CAD — cad. Parametric box with derived volume."""
from dcs.generate import requirement

def box(w: float, h: float, d: float) -> dict:
    return {"kind": "box", "w": w, "h": h, "d": d,
            "volume": w * h * d, "vertices": 8}

@requirement(id="DCS-CAD-001", title="box volume is w*h*d",
             section="CAD.cad", hats=["CAD"], criticality="MUST")
def test():
    b = box(2, 3, 4)
    assert b["volume"] == 24 and b["vertices"] == 8

