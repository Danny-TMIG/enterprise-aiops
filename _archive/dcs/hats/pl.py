"""PL — pl design. Grammar surface is documented and non-empty."""

from dcs.generate import requirement  # pragma: no cover

GRAMMAR = """
expr    : term (('+' | '-') term)*
term    : factor (('*' | '/') factor)*
factor  : NUMBER | '(' expr ')'
NUMBER  : /[0-9]+/
"""


def rules() -> list[str]:  # pragma: no cover
    return [  # pragma: no cover
        ln.split(":")[0].strip()
        for ln in GRAMMAR.splitlines()
        if ":" in ln and not ln.lstrip().startswith("NUMBER")  # pragma: no cover
    ]


@requirement(
    id="DCS-PL-001",
    title="grammar exposes expr/term/factor",
    section="PL.pldesign",
    hats=["PL"],
    criticality="MUST",
)
def test():  # pragma: no cover
    r = rules()
    assert "expr" in r and "term" in r and "factor" in r
