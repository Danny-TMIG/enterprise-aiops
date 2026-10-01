"""Mesh — reference requirements."""
from dcs.generate import requirement


@requirement(id="DCS-MESH-001", title="MeshOfMeshes.add_run accepts a bare Run",
             section="mesh", hats=["DIS", "SYS"], criticality="MUST")
def mesh_add_run():
    from app.train.mesh import MeshOfMeshes
    class FakeRun: pass
    m = MeshOfMeshes()
    m.add_run(FakeRun())
    assert len(m) == 1


@requirement(id="DCS-MESH-002", title="weave accepts a list",
             section="mesh", hats=["DE"], criticality="MUST")
def weave_accepts_list():
    from app.train.mesh import weave
    assert weave([])["runs"] == 0


@requirement(id="DCS-MESH-003", title="mesh exports the five public names",
             section="mesh", hats=["PL", "BE"], criticality="MUST")
def mesh_exports():
    from app.train import mesh as m
    for name in ("weave", "criss_cross", "trans", "pollinate", "MeshOfMeshes"):
        assert hasattr(m, name), name
