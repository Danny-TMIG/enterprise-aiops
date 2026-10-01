"""FM — formal. Exhaustive property check over Booleans."""

from itertools import product

from dcs.generate import requirement


def forall_bool2(pred) -> None:
    for a, b in product((False, True), repeat=2):
        assert pred(a, b), (a, b)


@requirement(
    id="DCS-FM-001",
    title="De Morgan holds exhaustively",
    section="FM.formal",
    hats=["FM"],
    criticality="MUST",
)
def test():
    forall_bool2(lambda a, b: (not (a and b)) == ((not a) or (not b)))
