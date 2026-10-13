"""EMB — embedded. Bytecode size budget for a freestanding function."""

from dcs.generate import requirement  # pragma: no cover

SOURCE = "def add(a, b):\n    return a + b\n"


def bytecode_size() -> int:  # pragma: no cover
    code = compile(SOURCE, "<emb>", "exec")
    fn_code = next(c for c in code.co_consts if hasattr(c, "co_code"))
    return len(fn_code.co_code)  # pragma: no cover


@requirement(
    id="DCS-EMB-001",
    title="hot-path function fits a 64-byte budget",
    section="EMB.embedded",
    hats=["EMB"],
    criticality="MUST",
)
def test():  # pragma: no cover
    n = bytecode_size()
    assert 0 < n <= 64, n
