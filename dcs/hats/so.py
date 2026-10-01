"""SO — sec offensive. Fuzz harness swallows expected parse errors."""

import random

from dcs.generate import requirement


def target(blob: bytes) -> dict:
    """Parser that should never crash on arbitrary input."""
    if not blob:
        return {"empty": True}
    if len(blob) > 32:
        raise ValueError("too long")
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError as err:
        raise ValueError("bad encoding") from err
    return {"len": len(text)}


def fuzz(n=200, seed=0) -> int:
    rng = random.Random(seed)
    for _ in range(n):
        try:
            target(rng.randbytes(rng.randint(0, 48)))
        except ValueError:
            continue
        except Exception as e:
            raise AssertionError(f"uncaught {type(e).__name__}: {e}") from e
    return n


@requirement(
    id="DCS-SO-001",
    title="fuzz harness raises only ValueError",
    section="SO.offensive",
    hats=["SO"],
    criticality="MUST",
)
def test():
    assert fuzz(200, seed=7) == 200
