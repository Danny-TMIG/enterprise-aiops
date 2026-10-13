"""DE — data eng. Topological DAG execution."""

from dcs.generate import requirement  # pragma: no cover


def run_dag(steps, ctx):  # pragma: no cover
    done = set()
    while len(done) < len(steps):
        progressed = False
        for name, deps, fn in steps:
            if name in done:  # pragma: no cover
                continue
            if all(d in done for d in deps):  # pragma: no cover
                ctx[name] = fn(ctx)
                done.add(name)
                progressed = True
        if not progressed:  # pragma: no cover
            raise RuntimeError(f"cycle or missing dep among {steps}")  # pragma: no cover
    return ctx  # pragma: no cover


@requirement(
    id="DCS-DE-001",
    title="DAG executes in dependency order",
    section="DE.dataeng",
    hats=["DE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    steps = [
        ("load", [], lambda c: 10),
        ("clean", ["load"], lambda c: c["load"] + 1),
        ("emit", ["clean"], lambda c: c["clean"] * 2),
    ]
    out = run_dag(steps, {})
    assert out["emit"] == 22, out
