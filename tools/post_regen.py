"""Restore core.py + mesh.py patches that the generator omits."""
import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── core.py ──────────────────────────────────────────────────────
cp = ROOT / "app/train/core.py"
src = cp.read_text()
tree = ast.parse(src)
lines = src.splitlines(keepends=True)

run_cls = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Run"), None)
needs_run = run_cls and "parent_id" not in src
if needs_run:
    new_run = '''@dataclass
class Run:
    index: int
    tiles: List[TrainTile]
    outcomes: List[TrainOutcome]
    duration_ms: float
    digest: str
    parent_id: Optional[str] = None

    @property
    def id(self) -> str:
        return self.digest

    @property
    def rates(self) -> dict:
        return {t.kind + "/" + t.solver + "/" + t.difficulty: t.rate for t in self.tiles}

    def to_dict(self):
        return {"index": self.index, "id": self.id, "parent_id": self.parent_id,
                "digest": self.digest, "duration_ms": round(self.duration_ms, 2),
                "tiles": [t.to_dict() for t in self.tiles],
                "outcomes": [o.to_dict() for o in self.outcomes]}
'''
    start = run_cls.lineno - 1
    if start > 0 and lines[start - 1].lstrip().startswith("@"):
        start -= 1
    lines = lines[:start] + [new_run, "\n"] + lines[run_cls.end_lineno:]

src = "".join(lines)
tree = ast.parse(src)
trainer = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Trainer"), None)
run_once = next((n for n in trainer.body if isinstance(n, ast.FunctionDef) and n.name == "run_once"), None)
if run_once and "parent_id" not in src.splitlines()[run_once.lineno-1:run_once.end_lineno] .__str__():
    new_run_once = '''    def run_once(self, index: int) -> Run:
        t0 = time.time()
        jobs = []
        for kind in self.cfg.kinds:
            for solver in sorted(SOLVERS.get(kind, {}).keys()):
                for difficulty in self.cfg.difficulties:
                    for pid in range(self.cfg.puzzles_per_tile):
                        jobs.append((kind, solver, difficulty, self.cfg.seed + index, pid))
        outcomes = [self._one(*j) for j in jobs]
        agg = {}
        for o in outcomes:
            k = (o.kind, o.solver, o.difficulty)
            cell = agg.setdefault(k, [0, 0]); cell[0] += 1
            if o.passed: cell[1] += 1
        tiles = [TrainTile(kind=k, solver=s, difficulty=d, trials=n, passes=p, duration_ms=0.0)
                 for (k, s, d), (n, p) in sorted(agg.items())]
        digest = _h("run", str(index), *sorted(t.digest for t in outcomes))
        pid = getattr(self, "last_run", None)
        parent_id = pid.digest if pid is not None else None
        run = Run(index=index, tiles=tiles, outcomes=outcomes,
                  duration_ms=(time.time()-t0)*1000.0, digest=digest, parent_id=parent_id)
        self.last_run = run
        return run
'''
    lines = src.splitlines(keepends=True)
    lines = lines[:run_once.lineno-1] + [new_run_once, "\n"] + lines[run_once.end_lineno:]
    src = "".join(lines)

# ensure _evolve + step exist
if "def _evolve(" not in src:
    src = src.rstrip() + '''


def _evolve(cfg, prev, index):
    all_diff = ["easy", "medium", "hard"]
    new_diff = [all_diff[index % 3], all_diff[(index + 1) % 3]]
    kinds = list(getattr(cfg, "kinds", [])) or ["sudoku"]
    return replace(cfg, kinds=kinds, difficulties=new_diff,
                   puzzles_per_tile=min(getattr(cfg, "puzzles_per_tile", 1) + 1, 8))
'''
if "    def step(" not in src:
    tree = ast.parse(src)
    trainer = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Trainer")
    end_line = max(n.end_lineno for n in trainer.body)
    lines = src.splitlines(keepends=True)
    step = "\n    def step(self, index):\n        run = self.run_once(index)\n        self.cfg = _evolve(self.cfg, run, index)\n        return run\n"
    lines = lines[:end_line] + [step] + lines[end_line:]
    src = "".join(lines)

cp.write_text(src)
ast.parse(src)
print("post_regen: core.py ok")

# ── mesh.py ──────────────────────────────────────────────────────
mp = ROOT / "app/train/mesh.py"
ms = mp.read_text()

def rt(s, name, body):
    pat = re.compile(rf"^def {re.escape(name)}\s*\([^\n]*\)[^\n]*:\n(?:.*\n)*?(?=^def |^class |\Z)", re.MULTILINE)
    return pat.sub(body.rstrip() + "\n\n", s, count=1) if pat.search(s) else s.rstrip() + "\n\n\n" + body.rstrip() + "\n"

ms = rt(ms, "weave", '''def weave(*args):
    runs = list(args[0]) if len(args) == 1 and isinstance(args[0], (list, tuple)) else list(args)
    return {"runs": len(runs),
            "outcomes": sum(len(getattr(r, "outcomes", [])) for r in runs),
            "digests": [getattr(r, "digest", None) for r in runs]}
''')

ms = re.sub(r"(?s)^    def add_run\(self.*?(?=^    def |^    @|^\S|\Z)",
            "    def add_run(self, run) -> None:\n        self.runs.append(run)\n\n",
            ms, count=1, flags=re.MULTILINE)

mp.write_text(ms)
ast.parse(ms)
print("post_regen: mesh.py ok")
