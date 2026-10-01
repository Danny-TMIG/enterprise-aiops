#!/usr/bin/env bash
set -euo pipefail
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

echo "=== 1. show what app/train/cli.py expects from trans() ==="
grep -nE "tr\[|tr\.get|trans\(" app/train/cli.py

echo
echo "=== 2. patch trans() to include 'reach' and 'digests' aliases ==="
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
    # backward-compat aliases for older cli.py expectations
    return {
        "digests": keys,          # legacy
        "keys": keys,
        "edges": edges,
        "transitive_pairs": transitive_pairs,
        "reachable": reachable,
        "reach": reachable,       # legacy
    }
'''

src2 = "".join(lines[:start]) + new + "".join(lines[end:])
compile(src2, str(p), "exec")
p.write_text(src2)
print("OK: trans() returns digests, keys, edges, transitive_pairs, reachable, reach")
PY

echo
echo "=== 3. smoke test ==="
python3 - <<'PY'
from app.train.core import TrainConfig, Trainer
from app.train.mesh import trans
cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0)
tr = Trainer(cfg)
runs = [tr.run_once(index=i) for i in range(4)]
out = trans(runs)
print("keys:      ", out["keys"])
print("edges:     ", out["edges"])
print("pairs:     ", out["transitive_pairs"])
print("reach:     ", out["reach"])
print("reachable: ", out["reachable"])
PY

echo
echo "=== 4. CLI ==="
python3 -m app.train.cli 2>&1 | tail -60
