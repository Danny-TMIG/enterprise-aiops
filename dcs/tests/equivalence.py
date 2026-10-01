"""Equivalence + coalescence requirements."""
from dcs.generate import requirement


@requirement(id="DCS-EQ-001", title="every artifact kind has an equivalence relation",
             section="equivalence", hats=["FM", "PL"], criticality="MUST")
def every_kind_registered():
    from dcs import equivalence
    expected = {
        "TrainTile", "TrainOutcome", "Run", "RunSequence",
        "MeshOfMeshes", "Weave", "CrissCross", "Pollinate",
        "Requirement", "Standard", "Bundle", "LogEntry", "LogChain",
        "dict", "JSON", "JSONList", "Dict", "FloatDict", "Bytes",
        "TileList", "OutcomeList",
    }
    missing = expected - set(equivalence.kinds())
    assert not missing, missing


@requirement(id="DCS-EQ-002", title="exact implies semantic for every kind",
             section="equivalence", hats=["FM", "SCI"], criticality="MUST")
def exact_implies_semantic():
    from dcs.equivalence import exact, semantic
    from app.train.core import TrainConfig, Trainer
    from app.train import mesh as _mesh
    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"],
                             puzzles_per_tile=1, seed=0))
    r0, r1 = tr.step(0), tr.step(1)
    samples = {
        "Run": (r0, r0),
        "RunSequence": ([r0, r1], [r0, r1]),
        "MeshOfMeshes": (_mesh.MeshOfMeshes([r0]), _mesh.MeshOfMeshes([r0])),
        "Weave": (_mesh.weave([r0]), _mesh.weave([r0])),
        "CrissCross": (_mesh.criss_cross(r0, r1), _mesh.criss_cross(r0, r1)),
        "Pollinate": (_mesh.pollinate(r0, r1), _mesh.pollinate(r0, r1)),
    }
    for kind, (a, b) in samples.items():
        if exact(kind, a, b):
            assert semantic(kind, a, b), kind


@requirement(id="DCS-EQ-003", title="equivalence is reflexive, symmetric",
             section="equivalence", hats=["FM"], criticality="MUST")
def equivalence_is_relation():
    from dcs.equivalence import semantic
    from app.train.core import TrainConfig, Trainer
    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"],
                             puzzles_per_tile=1, seed=0))
    a, b = tr.step(0), tr.step(0)
    assert semantic("Run", a, a)
    assert semantic("Run", a, b) == semantic("Run", b, a)


@requirement(id="DCS-CO-001", title="every coalescible kind is registered",
             section="coalescence", hats=["FM", "PL"], criticality="MUST")
def every_coalesce_registered():
    from dcs import coalesce
    expected = {
        "TrainTile", "TrainOutcome", "Run", "RunSequence",
        "MeshOfMeshes", "CrissCross", "Pollinate",
        "Requirement", "Standard", "Bundle", "LogEntry", "LogChain",
        "TileList", "OutcomeList",
    }
    missing = expected - set(coalesce.ops())
    assert not missing, missing


@requirement(id="DCS-CO-002", title="mesh coalescence is commutative + idempotent",
             section="coalescence", hats=["DIS", "FM"], criticality="MUST")
def mesh_coalescence_laws():
    from dcs import coalesce, equivalence
    from app.train.core import TrainConfig, Trainer
    from app.train.mesh import MeshOfMeshes
    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"],
                             puzzles_per_tile=1, seed=0))
    r0, r1 = tr.step(0), tr.step(1)
    m_ab = coalesce.merge("MeshOfMeshes",
                          MeshOfMeshes([r0]), MeshOfMeshes([r1])).value
    m_ba = coalesce.merge("MeshOfMeshes",
                          MeshOfMeshes([r1]), MeshOfMeshes([r0])).value
    assert equivalence.semantic("MeshOfMeshes", m_ab, m_ba)
    m_aa = coalesce.merge("MeshOfMeshes",
                          MeshOfMeshes([r0]), MeshOfMeshes([r0])).value
    assert len(m_aa) == 1


@requirement(id="DCS-CO-003", title="run coalescence refuses disagreement",
             section="coalescence", hats=["FM", "SRE"], criticality="MUST")
def run_merge_rejects():
    from dcs import coalesce
    from app.train.core import TrainConfig, Trainer
    t1 = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"],
                             puzzles_per_tile=1, seed=0))
    t2 = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["hard"],
                             puzzles_per_tile=1, seed=0))
    try:
        coalesce.merge("Run", t1.step(0), t2.step(0))
    except ValueError:
        return
    raise AssertionError("merged disagreeing runs")


@requirement(id="DCS-CO-004", title="requirement coalescence takes stricter criticality",
             section="coalescence", hats=["CMP2", "FM"], criticality="MUST")
def requirement_stricter():
    from dcs import coalesce
    from dcs.standard import Requirement
    a = Requirement(id="X", title="t", section="s", hats=["BE"],
                    criticality="MAY", test="f")
    b = Requirement(id="X", title="t", section="s", hats=["BE"],
                    criticality="MUST", test="f")
    assert coalesce.merge("Requirement", a, b).value.criticality == "MUST"
    assert coalesce.merge("Requirement", b, a).value.criticality == "MUST"


@requirement(id="DCS-CO-005", title="bundle coalescence is pessimistic on conflict",
             section="coalescence", hats=["CMP2", "SD"], criticality="MUST")
def bundle_pessimistic():
    from dcs import coalesce
    from dcs.evidence import Bundle, RequirementResult

    def mk(p):
        b = Bundle(standard_ref="x@1", reference={"name": "r"},
                   started=0.0, completed=1.0,
                   results=[RequirementResult(id="R", criticality="MUST",
                                              pass_=p, duration_ms=0.0)])
        return b.seal().to_dict()
    a, b = mk(True), mk(False)
    assert coalesce.merge("Bundle", a, b).value.verdict() == "NON_CONFORMANT"
    assert coalesce.merge("Bundle", b, a).value.verdict() == "NON_CONFORMANT"
