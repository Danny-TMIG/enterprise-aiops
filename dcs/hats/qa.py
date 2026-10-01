"""QA — qa. Assertion helper with message propagation."""

from dcs.generate import requirement


def expect(cond, msg: str = "") -> None:
    if not cond:
        raise AssertionError(msg or "expectation failed")


@requirement(
    id="DCS-QA-001",
    title="expectation helper enforces and reports",
    section="QA.qa",
    hats=["QA"],
    criticality="MUST",
)
def test():
    expect(1 + 1 == 2)
    try:
        expect(False, "bad")
    except AssertionError as e:
        assert "bad" in str(e)
    else:
        raise AssertionError("expect did not raise")
