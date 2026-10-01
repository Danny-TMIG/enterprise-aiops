"""DA — dev advocate. Example snippets compile."""
from dcs.generate import requirement

def example_ok(snippet: str) -> bool:
    try:
        compile(snippet, "<example>", "exec"); return True
    except SyntaxError:
        return False

@requirement(id="DCS-DA-001", title="documented examples are syntactically valid",
             section="DA.devrel", hats=["DA"], criticality="MUST")
def test():
    assert example_ok("x = 1")
    assert not example_ok("x = ")

