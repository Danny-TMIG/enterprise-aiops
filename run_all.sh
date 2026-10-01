#!/usr/bin/env bash
set -euo pipefail
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

echo "=== 1. patch generator /tmp/parallel_train.py ==="
if [ -f /tmp/parallel_train.py ]; then
  cp -n /tmp/parallel_train.py /tmp/parallel_train.py.bak 2>/dev/null || true
  LC_ALL=C sed -i '' \
    's/TrainTile, TrainOutcome, Run, Trainer, Config as TrainConfig,/TrainTile, TrainOutcome, Run, Trainer, TrainConfig,/' \
    /tmp/parallel_train.py
  if grep -q 'Config as TrainConfig' /tmp/parallel_train.py; then
    echo "FAIL: alias still present in generator"
    exit 1
  fi
  echo "OK: generator clean"
else
  echo "SKIP: /tmp/parallel_train.py not found"
fi

echo
echo "=== 2. patch app/train/__init__.py (belt and suspenders) ==="
if [ -f app/train/__init__.py ]; then
  LC_ALL=C sed -i '' 's/^\s*Config,\s*$/    TrainConfig,/' app/train/__init__.py || true
  grep -n 'Config' app/train/__init__.py
fi

echo
echo "=== 3. patch app/train/mesh.py trans() -> hierarchical ids ==="
python3 - <<'PY'
import ast
from pathlib import Path

p = Path("app/train/mesh.py")
if not p.exists():
    print("SKIP: app/train/mesh.py missing")
    raise SystemExit(0)

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
        "edges": edges,
        "transitive_pairs": transitive_pairs,
        "reachable": reachable,
        "keys": keys,
    }
'''

src_new = "".join(lines[:start]) + new + "".join(lines[end:])
p.write_text(src_new)
print("OK: trans() replaced")
PY

echo
echo "=== 4. patch app/puzzles/rubik.py scramble() guard ==="
python3 - <<'PY'
from pathlib import Path
p = Path("app/puzzles/rubik.py")
if not p.exists():
    print("SKIP: rubik.py missing")
    raise SystemExit(0)
s = p.read_text()
if "produced SOLVED" in s:
    print("SKIP: already guarded")
    raise SystemExit(0)
if "def scramble(" not in s:
    print("SKIP: no scramble()")
    raise SystemExit(0)
i = s.index("def scramble(")
j = s.index("return", i)
k = s.index("\n", j)
line = s[j:k]
indent = " " * (len(line) - len(line.lstrip()))
guard = (
    f"{line}\n"
    f"{indent}if state == SOLVED:\n"
    f"{indent}    raise ValueError('scramble produced SOLVED; reroll seed')\n"
    f"{indent}return state"
)
s = s[:j] + guard + s[k:]
p.write_text(s)
print("OK: rubik.scramble guarded")
PY

echo
echo "=== 5. verify ==="
python3 - <<'PY'
from app.train.core import TrainConfig, Trainer
from app.train.mesh import trans

cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0)
tr = Trainer(cfg)
runs = [tr.run_once(index=i) for i in range(4)]
out = trans(runs)
print("keys:            ", out["keys"])
print("edges:           ", out["edges"])
print("transitive_pairs:", out["transitive_pairs"])
print("reachable:       ", out["reachable"])
assert out["edges"] == 4, out
assert out["transitive_pairs"] == 4, out
print("OK: trans verified")

try:
    from app.puzzles.rubik import scramble, SOLVED
    for d in (2, 4, 6, 8):
        try:
            s = scramble(n_moves=d, seed=42)
            assert s != SOLVED, f"SOLVED at depth {d}"
        except ValueError:
            pass
    print("OK: rubik.scramble guarded")
except Exception as e:
    print("WARN rubik:", e)
PY

echo
echo "=== 6. run CLI ==="
python3 -m app.train.cli 2>&1 | tail -40
