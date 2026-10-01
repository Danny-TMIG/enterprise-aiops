"""Saga: compensating transactions."""
from dcs.generate import requirement

class Saga:
    def __init__(self):
        self.steps = []
    def add(self, do, undo):
        self.steps.append((do, undo)); return self
    def run(self, ctx):
        done = []
        try:
            for do, _ in self.steps:
                do(ctx); done.append(_)
            return True
        except Exception:
            for undo in reversed(done):
                undo(ctx)
            return False

@requirement(id="DCS-XC-SAGA-001", title="saga compensates in reverse order",
             section="X.saga", hats=["DIS", "DE"], criticality="MUST")
def test():
    log = []
    s = Saga() \
        .add(lambda c: log.append("do1"), lambda c: log.append("undo1")) \
        .add(lambda c: log.append("do2"), lambda c: log.append("undo2")) \
        .add(lambda c: (_ for _ in ()).throw(RuntimeError("boom")),
             lambda c: log.append("undo3"))
    assert s.run({}) is False
    assert log == ["do1", "do2", "undo2", "undo1"], log
