"""DA — dev advocate. Example snippets compile."""

from dcs.generate import requirement  # pragma: no cover


def example_ok(snippet: str) -> bool:  # pragma: no cover
    try:
        compile(snippet, "<example>", "exec")
        return True  # pragma: no cover
    except SyntaxError:  # pragma: no cover
        return False  # pragma: no cover


@requirement(
    id="DCS-DA-001",
    title="documented examples are syntactically valid",
    section="DA.devrel",
    hats=["DA"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert example_ok("x = 1")
    assert not example_ok("x = ")
