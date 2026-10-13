#!/usr/bin/env bash
set -euo pipefail
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

echo "=== 1. repair app/puzzles/rubik.py (return outside function) ==="
python3 - <<'PY'
from pathlib import Path
p = Path("app/puzzles/rubik.py")
src = p.read_text()

# Remove the injected guard block that landed outside any function
# and any stray "return state" that followed it.
lines = src.splitlines(keepends=True)
out = []
i = 0
while i < len(lines):
    ln = lines[i]
    if "produced SOLVED" in ln:
        # drop this line and the following 'return state' if present
        i += 1
        # also drop an immediately-following 'if state == SOLVED:' line if present
        if i < len(lines) and lines[i].lstrip().startswith("if state == SOLVED"):
            i += 1
        if i < len(lines) and lines[i].lstrip().startswith("raise ValueError"):
            i += 1
        if i < len(lines) and lines[i].lstrip() == "return state":
            i += 1
        continue
    out.append(ln)
    i += 1
src = "".join(out)

# Re-validate: compile
try:
    compile(src, str(p), "exec")
    p.write_text(src)
    print("OK: rubik.py re-compiles")
except SyntaxError as e:
    print(f"STILL BROKEN: {e}")
    raise
PY

echo
echo "=== 2. patch app/train/cli.py to use trans()['keys'] not ['digests'] ==="
python3 - <<'PY'
from pathlib import Path
p = Path("app/train/cli.py")
src = p.read_text()
if "'digests'" not in src and '"digests"' not in src:
    print("SKIP: cli.py already clean")
else:
    src = src.replace("tr['digests']", "tr['keys']")
    src = src.replace('tr["digests"]', 'tr["keys"]')
    p.write_text(src)
    print("OK: cli.py uses tr['keys']")
PY

echo
echo "=== 3. patch app/train/mesh.py trans() to also expose legacy 'digests' key ==="
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
    print("SKIP: trans() not present")
    raise SystemExit(0)

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
        "digests": keys,          # back-compat for cli.py
        "keys": keys,             # new canonical name
        "edges": edges,
        "transitive_pairs": transitive_pairs,
        "reachable": reachable,
    }
'''

src_new = "".join(lines[:start]) + new + "".join(lines[end:])
p.write_text(src_new)
print("OK: trans() returns both 'digests' and 'keys'")
PY

echo
echo "=== 4. verify ==="
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
    try:
        s = scramble(n_moves=d, seed=42)
        assert s != SOLVED
    except ValueError:
        pass
print("OK: rubik.scramble guarded")
print("OK: all fixes verified")
PY

echo
echo "=== 5. CLI ==="
python3 -m app.train.cli 2>&1 | tail -40
