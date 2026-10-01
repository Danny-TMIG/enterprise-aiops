"""TW — tech writer. Deterministic table of contents."""
from dcs.generate import requirement

def toc(sections: list[str]) -> str:
    return "\n".join(f"- [{s}](#{s.lower().replace(' ', '-')})" for s in sections)

@requirement(id="DCS-TW-001", title="TOC anchors are kebab-cased",
             section="TW.techwriter", hats=["TW"], criticality="MUST")
def test():
    md = toc(["Getting Started", "API Reference"])
    assert md == "- [Getting Started](#getting-started)\n- [API Reference](#api-reference)"

