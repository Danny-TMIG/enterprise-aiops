"""Accessibility: contrast ratio check per WCAG 2.1 AA."""
from dcs.generate import requirement

def luminance(rgb: tuple[int,int,int]) -> float:
    def ch(c):
        c /= 255
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    r, g, b = (ch(x) for x in rgb)
    return 0.2126*r + 0.7152*g + 0.0722*b

def contrast(fg: tuple, bg: tuple) -> float:
    l1, l2 = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)

@requirement(id="DCS-XC-A11Y-001", title="black-on-white clears WCAG AA 4.5:1",
             section="X.a11y", hats=["FE", "GFX", "QA"], criticality="MUST")
def test():
    assert contrast((0,0,0), (255,255,255)) >= 4.5
    assert contrast((255,255,255), (255,255,0)) < 4.5
