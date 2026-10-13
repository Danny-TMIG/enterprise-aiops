"""Train pipeline — reference requirements."""

import ast
from pathlib import Path

from dcs.generate import requirement

ROOT = Path(__file__).resolve().parent.parent.parent


@requirement(
    id="DCS-TRAIN-001",
    title="Run carries parent_id",
    section="train",
    hats=["BE", "DE", "FM"],
    criticality="MUST",
)
def run_has_parent_id():
    src = (ROOT / "app/train/core.py").read_text()
    tree = ast.parse(src)
    run = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Run")
    fields = [n.target.id for n in run.body if isinstance(n, ast.AnnAssign)]
    assert "parent_id" in fields, fields


@requirement(
    id="DCS-TRAIN-002",
    title="Trainer exposes step + _evolve",
    section="train",
    hats=["BE", "MLE", "FM"],
    criticality="MUST",
)
def trainer_has_step():
    src = (ROOT / "app/train/core.py").read_text()
    assert "def step(" in src
    assert "def _evolve(" in src


@requirement(
    id="DCS-TRAIN-003",
    title="trans produces an edge chain",
    section="train",
    hats=["DIS", "DE"],
    criticality="MUST",
)
def trans_produces_chain():
    from app.train.core import TrainConfig, Trainer
    from app.train.mesh import trans

    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    r0, r1, r2 = tr.step(0), tr.step(1), tr.step(2)
    out = trans([r0, r1, r2])
    assert out["edges"] == 2, out
    assert out["transitive_pairs"] == 3, out


@requirement(
    id="DCS-TRAIN-004",
    title="pollinate emits change deltas",
    section="train",
    hats=["DE", "DS"],
    criticality="MUST",
)
def pollinate_reports_change():
    from app.train.core import TrainConfig, Trainer
    from app.train.mesh import pollinate

    tr = Trainer(
        TrainConfig(
            kinds=["sudoku", "tictactoe"],
            difficulties=["easy", "medium"],
            puzzles_per_tile=1,
            seed=0,
        )
    )
    r0, r1 = tr.step(0), tr.step(1)
    pairs = pollinate(r0, r1)
    for p in pairs:
        assert set(p) == {"stream", "change", "a", "b", "delta"}
        assert p["change"] in {"added", "removed", "changed"}


@requirement(
    id="DCS-TRAIN-005",
    title="CLI runs to completion",
    section="train",
    hats=["BE", "TW", "QA"],
    criticality="MUST",
)
def cli_runs():
    import subprocess
    import sys

    r = subprocess.run(
        [sys.executable, "-m", "app.train.cli"], capture_output=True, text=True, cwd=str(ROOT)
    )
    assert r.returncode == 0, r.stderr[-400:]
    assert "resolution" in r.stdout
