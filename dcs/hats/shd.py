"""SHD — shader. GLSL string passes a structural check."""

from dcs.generate import requirement  # pragma: no cover


def fragment() -> str:  # pragma: no cover
    return "#version 330 core\nout vec4 color;\nvoid main() { color = vec4(1.0, 0.5, 0.2, 1.0); }\n"  # pragma: no cover


def structural_ok(src: str) -> bool:  # pragma: no cover
    return "#version" in src and "void main()" in src and src.count("{") == src.count("}")  # pragma: no cover


@requirement(
    id="DCS-SHD-001",
    title="fragment shader is structurally sound",
    section="SHD.shader",
    hats=["SHD"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert structural_ok(fragment())
