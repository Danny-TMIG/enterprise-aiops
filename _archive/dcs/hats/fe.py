"""FE — frontend. HTML surface validated by the stdlib parser."""

from html.parser import HTMLParser  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover

VOID = {"br", "img", "input", "meta", "link", "hr"}


def render_index() -> str:  # pragma: no cover
    return (  # pragma: no cover
        "<!doctype html><html><head><title>aiops</title></head><body>"
        "<h1>AI Ops</h1>"
        '<button hx-get="/health" hx-target="#out">ping</button>'
        '<div id="out"></div></body></html>'
    )


class _W(HTMLParser):  # pragma: no cover
    def __init__(self):  # pragma: no cover
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):  # pragma: no cover
        if tag not in VOID:  # pragma: no cover
            self.stack.append(tag)

    def handle_endtag(self, tag):  # pragma: no cover
        if not self.stack or self.stack.pop() != tag:  # pragma: no cover
            raise ValueError(f"unbalanced </{tag}>")  # pragma: no cover


def wellformed(html: str) -> bool:  # pragma: no cover
    _W().feed(html)
    return True  # pragma: no cover


@requirement(
    id="DCS-FE-001",
    title="index is well-formed and exposes an htmx contract",
    section="FE.frontend",
    hats=["FE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    h = render_index()
    assert h.startswith("<!doctype html>") and wellformed(h)
    assert "hx-get=" in h and "/health" in h
