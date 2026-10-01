"""SHD — shader. GLSL string passes a structural check."""
from dcs.generate import requirement

def fragment() -> str:
    return (
        "#version 330 core\n"
        "out vec4 color;\n"
        "void main() { color = vec4(1.0, 0.5, 0.2, 1.0); }\n"
    )

def structural_ok(src: str) -> bool:
    return ("#version" in src
            and "void main()" in src
            and src.count("{") == src.count("}"))

@requirement(id="DCS-SHD-001", title="fragment shader is structurally sound",
             section="SHD.shader", hats=["SHD"], criticality="MUST")
def test():
    assert structural_ok(fragment())

