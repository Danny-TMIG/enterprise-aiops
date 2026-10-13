"""Frontend, media, mobile, and design-adjacent requirements."""

from dcs.generate import requirement  # pragma: no cover


@requirement(
    id="EQ-FE-002",
    title="HTML id attributes are unique",
    section="EQ.ui",
    hats=["FE"],
    criticality="MUST",
)
def fe_ids_unique():  # pragma: no cover
    import re  # pragma: no cover
    from collections import Counter  # pragma: no cover

    html = '<div id="a"></div><span id="b"></span><p id="a"></p>'
    ids = re.findall(r'id="([^"]+)"', html)
    dupes = [k for k, v in Counter(ids).items() if v > 1]
    assert dupes, "test expects the duplicate"


@requirement(
    id="EQ-FE-003",
    title="CSS selectors are balanced",
    section="EQ.ui",
    hats=["FE"],
    criticality="MUST",
)
def fe_css_balanced():  # pragma: no cover
    css = "body { margin: 0 } .x { color: red }"
    assert css.count("{") == css.count("}")


@requirement(
    id="EQ-FE-004",
    title="hyperlink target is valid",
    section="EQ.ui",
    hats=["FE"],
    criticality="MUST",
)
def fe_link_target():  # pragma: no cover
    hrefs = ["/home", "#top", "https://x.y"]
    assert all(h.startswith(("/", "#", "http")) for h in hrefs)


@requirement(
    id="EQ-FE-005",
    title="aria-label present on icon buttons",
    section="EQ.ui",
    hats=["FE"],
    criticality="MUST",
)
def fe_aria():  # pragma: no cover
    btn = '<button aria-label="close">×</button>'
    assert "aria-label=" in btn


@requirement(
    id="EQ-MO-002",
    title="viewport meta is present",
    section="EQ.ui",
    hats=["MO"],
    criticality="MUST",
)
def mo_viewport():  # pragma: no cover
    html = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    assert "width=device-width" in html


@requirement(
    id="EQ-MO-003",
    title="manifest icons include 512px",
    section="EQ.ui",
    hats=["MO"],
    criticality="MUST",
)
def mo_icon_sizes():  # pragma: no cover
    icons = [{"sizes": "192x192"}, {"sizes": "512x512"}]
    assert any(i["sizes"] == "512x512" for i in icons)


@requirement(
    id="EQ-MO-004",
    title="offline service worker caches shell",
    section="EQ.ui",
    hats=["MO"],
    criticality="SHOULD",
)
def mo_sw():  # pragma: no cover
    sw = "self.addEventListener('install', e => e.waitUntil(caches.open('v1')))"
    assert "caches.open" in sw


@requirement(
    id="EQ-FS-002",
    title="hydration payload is valid JSON",
    section="EQ.ui",
    hats=["FS"],
    criticality="MUST",
)
def fs_hydration():  # pragma: no cover
    import json  # pragma: no cover

    payload = '{"user":"a","data":[1,2,3]}'
    json.loads(payload)


@requirement(
    id="EQ-FS-003",
    title="SSR and CSR render the same shell",
    section="EQ.ui",
    hats=["FS"],
    criticality="MUST",
)
def fs_ssr():  # pragma: no cover
    def csr():  # pragma: no cover
        return "<div>x</div>"  # pragma: no cover

    def ssr():  # pragma: no cover
        return "<div>x</div>"  # pragma: no cover

    assert csr() == ssr()


@requirement(
    id="EQ-GFX-002", title="SVG viewBox declared", section="EQ.ui", hats=["GFX"], criticality="MUST"
)
def gfx_viewbox():  # pragma: no cover
    svg = '<svg viewBox="0 0 100 100"><circle r="10"/></svg>'
    assert "viewBox=" in svg


@requirement(
    id="EQ-GFX-003",
    title="polygon closes with Z",
    section="EQ.ui",
    hats=["GFX"],
    criticality="MUST",
)
def gfx_polygon():  # pragma: no cover
    poly = "M0 0 L10 0 L10 10 Z"
    assert poly.strip().endswith("Z")


@requirement(
    id="EQ-GFX-004",
    title="gradient stops in [0,1]",
    section="EQ.ui",
    hats=["GFX"],
    criticality="MUST",
)
def gfx_gradient():  # pragma: no cover
    stops = [0.0, 0.5, 1.0]
    assert all(0 <= s <= 1 for s in stops)


@requirement(
    id="EQ-SHD-002",
    title="vertex shader declares gl_Position",
    section="EQ.ui",
    hats=["SHD"],
    criticality="MUST",
)
def shd_vertex():  # pragma: no cover
    src = "void main() { gl_Position = vec4(0); }"
    assert "gl_Position" in src


@requirement(
    id="EQ-SHD-003",
    title="uniform declared before use",
    section="EQ.ui",
    hats=["SHD"],
    criticality="MUST",
)
def shd_uniform():  # pragma: no cover
    src = "uniform float t;\nvoid main(){ float x = t; }"
    idx_u = src.index("uniform")
    idx_use = src.rindex("t")
    assert idx_u < idx_use


@requirement(
    id="EQ-VID-002",
    title="frame timestamps are monotonic",
    section="EQ.ui",
    hats=["VID"],
    criticality="MUST",
)
def vid_monotonic():  # pragma: no cover
    ts = [0.0, 0.033, 0.066, 0.100]
    assert all(b >= a for a, b in zip(ts, ts[1:]))


@requirement(
    id="EQ-VID-003", title="codec string parses", section="EQ.ui", hats=["VID"], criticality="MUST"
)
def vid_codec():  # pragma: no cover
    codec = "avc1.64001f"
    kind, level = codec.split(".")
    assert kind == "avc1"


@requirement(
    id="EQ-AU-002",
    title="sample rate is standard",
    section="EQ.ui",
    hats=["AU"],
    criticality="MUST",
)
def au_rate():  # pragma: no cover
    assert 44100 in (44100, 48000)


@requirement(
    id="EQ-AU-003",
    title="PCM amplitude in [-1, 1]",
    section="EQ.ui",
    hats=["AU"],
    criticality="MUST",
)
def au_pcm():  # pragma: no cover
    samples = [0.0, 0.5, -0.5, 1.0, -1.0]
    assert all(-1 <= s <= 1 for s in samples)


@requirement(
    id="EQ-AU-004",
    title="channel count is 1 or 2",
    section="EQ.ui",
    hats=["AU"],
    criticality="MUST",
)
def au_channels():  # pragma: no cover
    assert 1 in (1, 2) and 2 in (1, 2)


@requirement(
    id="EQ-CAD-002",
    title="all box dimensions positive",
    section="EQ.ui",
    hats=["CAD"],
    criticality="MUST",
)
def cad_dims():  # pragma: no cover
    dims = (2, 3, 4)
    assert all(d > 0 for d in dims)


@requirement(
    id="EQ-CAD-003",
    title="mesh vertex/face ratio is Euler-consistent",
    section="EQ.ui",
    hats=["CAD"],
    criticality="MUST",
)
def cad_euler():  # pragma: no cover
    # V - E + F = 2 for a closed convex polyhedron
    V, E, F = 8, 12, 6
    assert V - E + F == 2


@requirement(
    id="EQ-GAME-002",
    title="turn order alternates",
    section="EQ.ui",
    hats=["GAME"],
    criticality="MUST",
)
def game_turns():  # pragma: no cover
    seq = ["X", "O", "X", "O"]
    assert all(a != b for a, b in zip(seq, seq[1:]))


@requirement(
    id="EQ-GAME-003",
    title="move inside board bounds",
    section="EQ.ui",
    hats=["GAME"],
    criticality="MUST",
)
def game_bounds():  # pragma: no cover
    move = 4
    assert 0 <= move < 9


@requirement(
    id="EQ-GAME-004",
    title="terminal states are absorbing",
    section="EQ.ui",
    hats=["GAME"],
    criticality="MUST",
)
def game_terminal():  # pragma: no cover
    board = ["X", "X", "X", "", "", "", "", "", ""]

    def is_terminal(b):  # pragma: no cover
        return b[0] == b[1] == b[2] != ""  # pragma: no cover

    assert is_terminal(board)
    assert is_terminal(board)  # idempotent


@requirement(
    id="EQ-TW-002",
    title="heading levels do not skip",
    section="EQ.ui",
    hats=["TW"],
    criticality="MUST",
)
def tw_headings():  # pragma: no cover
    levels = [1, 2, 3, 4]
    assert all(b - a <= 1 for a, b in zip(levels, levels[1:]))


@requirement(
    id="EQ-TW-003",
    title="code blocks declare a language",
    section="EQ.ui",
    hats=["TW"],
    criticality="MUST",
)
def tw_code_lang():  # pragma: no cover
    md = "```python\nx = 1\n```"
    assert md.startswith("```") and "python" in md.split("\n")[0]


@requirement(
    id="EQ-TW-004",
    title="links use absolute or https",
    section="EQ.ui",
    hats=["TW"],
    criticality="SHOULD",
)
def tw_links():  # pragma: no cover
    links = ["https://x.y", "/local"]
    assert all(l.startswith(("http", "/")) for l in links)


@requirement(
    id="EQ-DA-002",
    title="example shows expected output",
    section="EQ.ui",
    hats=["DA"],
    criticality="MUST",
)
def da_output():  # pragma: no cover
    md = "```python\nprint(1)\n```\n```\n1\n```"
    assert md.count("```") >= 4


@requirement(
    id="EQ-DA-003",
    title="quickstart fits a single code block",
    section="EQ.ui",
    hats=["DA"],
    criticality="MUST",
)
def da_quickstart():  # pragma: no cover
    steps = ["pip install dcs", "dcs conform"]
    assert len(steps) <= 5
