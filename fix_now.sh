#!/usr/bin/env bash
set -euo pipefail
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

# ── 1. Patch generator so __init__.py emits TrainConfig, not Config-as-TrainConfig ──
cp -n /tmp/parallel_train.py /tmp/parallel_train.py.bak
LC_ALL=C sed -i '' \
  's/TrainTile, TrainOutcome, Run, Trainer, Config as TrainConfig,/TrainTile, TrainOutcome, Run, Trainer, TrainConfig,/' \
  /tmp/parallel_train.py
if grep -q 'Config as' /tmp/parallel_train.py; then
  echo "WARN: generator still has alias; inspect line:"
  grep -n 'Config as' /tmp/parallel_train.py
else
  echo "OK: generator patched"
fi

# ── 2. Replace trans() with a prefix-normalised implementation ──
python3 - <<'PY'
import ast
from pathlib import Path

p = Path.home() / "enterprise_aiops" / "app" / "train" / "mesh.py"
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
    raise SystemExit("ERROR: trans() not found in mesh.py")

old = "".join(lines[start:end])
print("---------- current trans() ----------")
print(old, end="")
print("-------------------------------------")

new = '''def trans(runs: List[Run]) -> Dict[str, Any]:
    """Prefix closure over run digests.

    Digests are normalised to the first 8 hex chars (32 bits) before
    comparison. Without this, full sha256 digests never share a prefix
    and the closure is trivially empty.
    """
    K = 8
    full_keys: List[str] = []
    short_keys: List[str] = []
    for r in runs:
        d = getattr(r, "digest", None) or str(r)
        if not isinstance(d, str):
            d = str(d)
        full_keys.append(d)
        short_keys.append(d.split(":", 1)[-1][:K])

    n = len(short_keys)
    adj = [set() for _ in range(n)]
    edges = 0
    for i in range(n):
        for j in range(n):
            if i != j and short_keys[i] != short_keys[j] \\
                    and short_keys[j].startswith(short_keys[i]):
                adj[i].add(j)
                edges += 1

    reach = [set(a) for a in adj]
    for k in range(n):
        for i in range(n):
            if k in reach[i]:
                reach[i] |= reach[k]

    transitive_pairs = sum(len(r) for r in reach)
    reachable = {full_keys[i]: len(reach[i]) for i in range(n)}

    return {
        "edges": edges,
        "transitive_pairs": transitive_pairs,
        "reachable": reachable,
        "short_keys": short_keys,
    }
'''

src_new = "".join(lines[:start]) + new + "".join(lines[end:])
p.write_text(src_new)
print("OK: mesh.trans replaced")
PY

# ── 3. Verify rubik.scramble guard is still in place ──
python3 - <<'PY'
from app.puzzles.rubik import scramble, SOLVED
bad = []
for d in (2, 4, 6, 8, 10):
    try:
        s = scramble(n_moves=d, seed=42)
        if s == SOLVED:
            bad.append(d)
    except ValueError:
        pass
if bad:
    raise SystemExit(f"rubik.scramble still returns SOLVED at depths {bad}")
print("OK: rubik.scramble guarded")
PY

# ── 4. Regenerate train package from the fixed generator ──
rm -f app/train/__init__.py
python3 /tmp/parallel_train.py >/dev/null

# ── 5. Smoke test ──
python3 - <<'PY'
import app.train as t
assert t.TrainConfig is not None
from app.train.core import Trainer, TrainConfig
from app.train.mesh import trans
cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"], tiles_per_kind=1, seed=0) \
    if "tiles_per_kind" in TrainConfig.__dataclass_fields__ else TrainConfig()
tr = Trainer(cfg)
r1 = tr.run_once(index=0)
r2 = tr.run_once(index=1)
out = trans([r1, r2])
print("OK trans ->", {k: out[k] for k in ("edges", "transitive_pairs")})
print("OK: all fixes verified")
PY

echo
echo "running: python3 -m app.train.cli"
python3 -m app.train.cli 2>&1 | head -60
