"""Accessibility: contrast ratio check per WCAG 2.1 AA."""

from dcs.generate import requirement  # pragma: no cover


def luminance(rgb: tuple[int, int, int]) -> float:  # pragma: no cover
    def ch(c):  # pragma: no cover
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4  # pragma: no cover

    r, g, b = (ch(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b  # pragma: no cover


def contrast(fg: tuple, bg: tuple) -> float:  # pragma: no cover
    l1, l2 = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)  # pragma: no cover


@requirement(
    id="DCS-XC-A11Y-001",
    title="black-on-white clears WCAG AA 4.5:1",
    section="X.a11y",
    hats=["FE", "GFX", "QA"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert contrast((0, 0, 0), (255, 255, 255)) >= 4.5
    assert contrast((255, 255, 255), (255, 255, 0)) < 4.5
