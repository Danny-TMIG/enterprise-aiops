"""QA — qa. Assertion helper with message propagation."""

from dcs.generate import requirement  # pragma: no cover


def expect(cond, msg: str = "") -> None:  # pragma: no cover
    if not cond:  # pragma: no cover
        raise AssertionError(msg or "expectation failed")  # pragma: no cover


@requirement(
    id="DCS-QA-001",
    title="expectation helper enforces and reports",
    section="QA.qa",
    hats=["QA"],
    criticality="MUST",
)
def test():  # pragma: no cover
    expect(1 + 1 == 2)
    try:
        expect(False, "bad")
    except AssertionError as e:  # pragma: no cover
        assert "bad" in str(e)
    else:
        raise AssertionError("expect did not raise")  # pragma: no cover
