"""SO — sec offensive. Fuzz harness swallows expected parse errors."""

import random  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def target(blob: bytes) -> dict:  # pragma: no cover
    """Parser that should never crash on arbitrary input."""
    if not blob:  # pragma: no cover
        return {"empty": True}  # pragma: no cover
    if len(blob) > 32:  # pragma: no cover
        raise ValueError("too long")  # pragma: no cover
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError as err:  # pragma: no cover
        raise ValueError("bad encoding") from err  # pragma: no cover
    return {"len": len(text)}  # pragma: no cover


def fuzz(n=200, seed=0) -> int:  # pragma: no cover
    rng = random.Random(seed)
    for _ in range(n):
        try:
            target(rng.randbytes(rng.randint(0, 48)))
        except ValueError:  # pragma: no cover
            continue
        except Exception as e:  # pragma: no cover
            raise AssertionError(f"uncaught {type(e).__name__}: {e}") from e  # pragma: no cover
    return n  # pragma: no cover


@requirement(
    id="DCS-SO-001",
    title="fuzz harness raises only ValueError",
    section="SO.offensive",
    hats=["SO"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert fuzz(200, seed=7) == 200
