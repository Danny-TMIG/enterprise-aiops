"""TW — tech writer. Deterministic table of contents."""

from dcs.generate import requirement  # pragma: no cover


def toc(sections: list[str]) -> str:  # pragma: no cover
    return "\n".join(f"- [{s}](#{s.lower().replace(' ', '-')})" for s in sections)  # pragma: no cover


@requirement(
    id="DCS-TW-001",
    title="TOC anchors are kebab-cased",
    section="TW.techwriter",
    hats=["TW"],
    criticality="MUST",
)
def test():  # pragma: no cover
    md = toc(["Getting Started", "API Reference"])
    assert md == "- [Getting Started](#getting-started)\n- [API Reference](#api-reference)"
