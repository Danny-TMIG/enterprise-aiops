"""Assertions that must hold for core.py and mesh.py to be correct."""
import ast
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

CHECKS = []

def check(name):
    def deco(fn):
        CHECKS.append((name, fn)); return fn
    return deco

@check("core.py has Run.parent_id")
def _(): 
    src = (ROOT/"app/train/core.py").read_text()
    tree = ast.parse(src)
    run = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name=="Run")
    fields = [n.target.id for n in run.body if isinstance(n, ast.AnnAssign)]
    assert "parent_id" in fields, f"Run fields: {fields}"

@check("core.py Trainer has step + _evolve")
def _():
    src = (ROOT/"app/train/core.py").read_text()
    assert "def step(" in src
    assert "def _evolve(" in src

@check("Run has id / rates / to_dict")
def _():
    from app.train.core import Run
    for m in ("id", "rates", "to_dict"):
        assert hasattr(Run, m), f"Run missing {m}"

@check("mesh.py exports weave/criss_cross/trans/pollinate/MeshOfMeshes")
def _():
    from app.train import mesh
    for m in ("weave", "criss_cross", "trans", "pollinate", "MeshOfMeshes"):
        assert hasattr(mesh, m), f"mesh missing {m}"

@check("weave accepts a list of runs")
def _():
    from app.train.mesh import weave
    r = weave([]); assert r["runs"] == 0

@check("MeshOfMeshes.add_run accepts a Run (no tile iteration)")
def _():
    from app.train.mesh import MeshOfMeshes
    m = MeshOfMeshes()
    class FakeRun: pass
    m.add_run(FakeRun())

@check("trans produces edges when parent_id chain present")
def _():
    from app.train.core import TrainConfig, Trainer
    from app.train.mesh import trans
    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    r0 = tr.step(0); r1 = tr.step(1); r2 = tr.step(2)
    out = trans([r0, r1, r2])
    assert out["edges"] == 2, out
    assert out["transitive_pairs"] == 3, out

@check("pollinate emits added/removed/changed between rotated runs")
def _():
    from app.train.core import TrainConfig, Trainer
    from app.train.mesh import pollinate
    tr = Trainer(TrainConfig(kinds=["sudoku", "tictactoe"], difficulties=["easy", "medium"], puzzles_per_tile=1, seed=0))
    r0 = tr.step(0); r1 = tr.step(1)
    pairs = pollinate(r0, r1)
    assert isinstance(pairs, list)
    for p in pairs:
        assert set(p) == {"stream", "change", "a", "b", "delta"}
        assert p["change"] in {"added", "removed", "changed"}

def run_all() -> int:
    failed = 0
    for name, fn in CHECKS:
        try:
            fn()
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {type(e).__name__}: {e}")
            failed += 1
    return failed

if __name__ == "__main__":
    importlib.invalidate_caches()
    print("invariants:")
    sys.exit(1 if run_all() else 0)
