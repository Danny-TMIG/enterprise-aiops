"""GFX — graphics. SVG generation."""

from dcs.generate import requirement


def bar_chart(values: list[float], w: int = 200, h: int = 80) -> str:
    mx = max(values) or 1.0
    bars = "".join(
        f'<rect x="{i * 20}" y="{h - v / mx * h}" width="18" height="{v / mx * h}"/>'
        for i, v in enumerate(values)
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">{bars}</svg>'


@requirement(
    id="DCS-GFX-001",
    title="SVG has one rect per data point",
    section="GFX.graphics",
    hats=["GFX"],
    criticality="MUST",
)
def test():
    svg = bar_chart([1, 2, 3, 4])
    assert svg.startswith("<svg") and svg.endswith("</svg>")
    assert svg.count("<rect") == 4
