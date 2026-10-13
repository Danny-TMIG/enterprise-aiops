#!/usr/bin/env bash
set -euo pipefail
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

echo "=== 1. rewrite rubik.scramble() with in-function guard ==="
python3 - <<'PY'
import re
from pathlib import Path

p = Path("app/puzzles/rubik.py")
src = p.read_text()

pattern = re.compile(
    r"^def scramble\([^\n]*\n(?:.*\n)*?(?=^def |^class |\Z)",
    re.MULTILINE,
)

new = '''def scramble(n_moves: int = 11, seed: int = 0) -> Tuple[int, ...]:
    rng = random.Random(seed)
    for _ in range(64):
        s = SOLVED
        for _ in range(n_moves):
            m = rng.choice(list(MOVES.keys()))
            s = apply_move(MOVES[m], s)
        if s != SOLVED:
            return s
    raise ValueError("scramble could not escape SOLVED in 64 attempts")


'''

if not pattern.search(src):
    raise SystemExit("ERROR: scramble() block not found")

src2 = pattern.sub(new, src, count=1)
compile(src2, str(p), "exec")
p.write_text(src2)
print("OK: rubik.scramble rewritten")
PY

echo
echo "=== 2. mesh.trans() returns BOTH 'keys' and 'digests' ==="
python3 - <<'PY'
import ast
from pathlib import Path

p = Path("app/train/mesh.py")
src = p.read_text()
tree = ast.parse(src)
lines = src.splitlines(keepends=True)

start = end = None
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name == "trans":
        start = (node.decorator_list[0].lineno - 1) if node.decorator_list else (node.lineno - 1)
        end = node.end_lineno
        break
if start is None:
    raise SystemExit("ERROR: trans() not found")

new = '''def _run_id(run, index):
    for attr in ("id", "run_id"):
        v = getattr(run, attr, None)
        if isinstance(v, str) and v:
            return v
    if index == 0:
        return "r"
    return "r." + ".".join(str(d) for d in _digits(index))


def _digits(n):
    if n < 3:
        return [n]
    out = []
    while n >= 3:
        out.append(1 + (n - 3) % 2)
        n = 1 + (n - 3) // 2
    out.append(n)
    return list(reversed(out))


def trans(runs, key_fn=None):
    keys = []
    for i, r in enumerate(runs):
        k = key_fn(r, i) if key_fn is not None else _run_id(r, i)
        keys.append(str(k))

    n = len(keys)
    adj = [set() for _ in range(n)]
    edges = 0
    for i in range(n):
        for j in range(n):
            if i != j and keys[j].startswith(keys[i] + "."):
                adj[i].add(j)
                edges += 1

    reach = [set(a) for a in adj]
    for k in range(n):
        for i in range(n):
            if k in reach[i]:
                reach[i] |= reach[k]

    transitive_pairs = sum(len(r) for r in reach)
    reachable = {keys[i]: len(reach[i]) for i in range(n)}
    return {
        "digests": keys,
        "keys": keys,
        "edges": edges,
        "transitive_pairs": transitive_pairs,
        "reachable": reachable,
    }
'''

src2 = "".join(lines[:start]) + new + "".join(lines[end:])
compile(src2, str(p), "exec")
p.write_text(src2)
print("OK: trans() returns digests + keys")
PY

echo
echo "=== 3. verify ==="
python3 - <<'PY'
from app.train.core import TrainConfig, Trainer
from app.train.mesh import trans
from app.puzzles.rubik import scramble, SOLVED

cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0)
tr = Trainer(cfg)
runs = [tr.run_once(index=i) for i in range(4)]
out = trans(runs)
print("keys:            ", out["keys"])
print("digests:         ", out["digests"])
print("edges:           ", out["edges"])
print("transitive_pairs:", out["transitive_pairs"])
assert out["edges"] == 4
assert out["transitive_pairs"] == 4

for d in (2, 4, 6, 8):
    s = scramble(n_moves=d, seed=42)
    assert s != SOLVED, f"scramble returned SOLVED at depth {d}"
print("OK: rubik.scramble safe")
print("OK: all fixes verified")
PY

echo
echo "=== 4. CLI ==="
python3 -m app.train.cli 2>&1 | tail -40
