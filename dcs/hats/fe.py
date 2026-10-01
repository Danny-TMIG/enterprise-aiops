"""FE — frontend. HTML surface validated by the stdlib parser."""
from html.parser import HTMLParser
from dcs.generate import requirement

VOID = {"br","img","input","meta","link","hr"}

def render_index() -> str:
    return ('<!doctype html><html><head><title>aiops</title></head><body>'
            '<h1>AI Ops</h1>'
            '<button hx-get="/health" hx-target="#out">ping</button>'
            '<div id="out"></div></body></html>')

class _W(HTMLParser):
    def __init__(self): super().__init__(); self.stack=[]
    def handle_starttag(self, tag, attrs):
        if tag not in VOID: self.stack.append(tag)
    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise ValueError(f"unbalanced </{tag}>")

def wellformed(html: str) -> bool:
    _W().feed(html); return True

@requirement(id="DCS-FE-001", title="index is well-formed and exposes an htmx contract",
             section="FE.frontend", hats=["FE"], criticality="MUST")
def test():
    h = render_index()
    assert h.startswith("<!doctype html>") and wellformed(h)
    assert "hx-get=" in h and "/health" in h

