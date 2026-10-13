"""FM — formal. Exhaustive property check over Booleans."""

from itertools import product  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def forall_bool2(pred) -> None:  # pragma: no cover
    for a, b in product((False, True), repeat=2):
        assert pred(a, b), (a, b)


@requirement(
    id="DCS-FM-001",
    title="De Morgan holds exhaustively",
    section="FM.formal",
    hats=["FM"],
    criticality="MUST",
)
def test():  # pragma: no cover
    forall_bool2(lambda a, b: (not (a and b)) == ((not a) or (not b)))
