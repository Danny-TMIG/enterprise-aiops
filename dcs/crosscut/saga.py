"""Saga: compensating transactions."""

from dcs.generate import requirement  # pragma: no cover


class Saga:  # pragma: no cover
    def __init__(self):  # pragma: no cover
        self.steps = []

    def add(self, do, undo):  # pragma: no cover
        self.steps.append((do, undo))
        return self  # pragma: no cover

    def run(self, ctx):  # pragma: no cover
        done = []
        try:
            for do, _ in self.steps:
                do(ctx)
                done.append(_)
            return True  # pragma: no cover
        except Exception:  # pragma: no cover
            for undo in reversed(done):
                undo(ctx)
            return False  # pragma: no cover


@requirement(
    id="DCS-XC-SAGA-001",
    title="saga compensates in reverse order",
    section="X.saga",
    hats=["DIS", "DE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    log = []
    s = (
        Saga()
        .add(lambda c: log.append("do1"), lambda c: log.append("undo1"))
        .add(lambda c: log.append("do2"), lambda c: log.append("undo2"))
        .add(lambda c: (_ for _ in ()).throw(RuntimeError("boom")), lambda c: log.append("undo3"))
    )
    assert s.run({}) is False
    assert log == ["do1", "do2", "undo2", "undo1"], log
