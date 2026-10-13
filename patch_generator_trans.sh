#!/usr/bin/env bash
# No set -e: we want to see every step even if one fails.
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

GEN=/tmp/parallel_train.py
[ -f "$GEN" ] || { echo "FAIL: $GEN missing"; exit 1; }

cp -n "$GEN" "${GEN}.bak2" 2>/dev/null
echo "[1] backup: ${GEN}.bak2"

echo "[2] patching generator trans() ..."
python3 - <<'PY'
from pathlib import Path
p = Path("/tmp/parallel_train.py")
src = p.read_text()

anchor = "def trans(runs: List[Run]) -> Dict[str, Any]:"
i = src.find(anchor)
if i == -1:
    raise SystemExit("FAIL: anchor not found")
print(f"    anchor at byte {i}")

# find end of the function: first top-level def/class/''' after anchor
j = src.find("\n", i) + 1
end = len(src)
while j < len(src):
    le = src.find("\n", j)
    if le == -1: le = len(src)
    line = src[j:le]
    if line.startswith(("def ", "class ", "'''", '"""')):
        end = j
        break
    j = le + 1
print(f"    function body ends at byte {end}")

new_fn = '''def _run_id(run, index):
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


def trans(runs: List[Run], key_fn=None) -> Dict[str, Any]:
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

    reach_sets = [set(a) for a in adj]
    for k in range(n):
        for i in range(n):
            if k in reach_sets[i]:
                reach_sets[i] |= reach_sets[k]

    transitive_pairs = sum(len(r) for r in reach_sets)
    reach = {keys[i]: [keys[j] for j in sorted(reach_sets[i])] for i in range(n)}
    reachable = {k: len(v) for k, v in reach.items()}
    return {
        "digests": keys,
        "keys": keys,
        "edges": edges,
        "transitive_pairs": transitive_pairs,
        "reachable": reachable,
        "reach": reach,
    }
'''

src2 = src[:i] + new_fn + src[end:]
p.write_text(src2)
print("    wrote generator")
PY

echo "[3] verify generator syntax"
python3 -c "import ast; ast.parse(open('$GEN').read()); print('    OK: syntax valid')" \
  || { echo "FAIL: generator syntax broken"; exit 1; }

echo "[4] grep new symbols in generator"
grep -c "_run_id" "$GEN" || true
grep -c "\"keys\":" "$GEN" || true

echo "[5] delete stale generated files"
rm -f app/train/__init__.py app/train/mesh.py app/train/core.py \
      app/train/cd_state.py app/train/publish.py app/train/driver.py \
      app/train/cli.py

echo "[6] regenerate train package"
python3 "$GEN" 2>&1 | tail -20
echo "    (parallel_train.py exit: $?)"

echo "[7] check generated mesh.py has correct trans()"
if grep -q '"_run_id"' app/train/mesh.py || grep -q '"keys"' app/train/mesh.py; then
  echo "    OK: regenerated mesh.py has new trans()"
else
  echo "    WARN: regenerated mesh.py has OLD trans(); patching in place"
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
    raise SystemExit("    FAIL: trans() not found in regenerated mesh.py")
new = '''def _run_id(run, index):
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

    reach_sets = [set(a) for a in adj]
    for k in range(n):
        for i in range(n):
            if k in reach_sets[i]:
                reach_sets[i] |= reach_sets[k]

    transitive_pairs = sum(len(r) for r in reach_sets)
    reach = {keys[i]: [keys[j] for j in sorted(reach_sets[i])] for i in range(n)}
    reachable = {k: len(v) for k, v in reach.items()}
    return {
        "digests": keys,
        "keys": keys,
        "edges": edges,
        "transitive_pairs": transitive_pairs,
        "reachable": reachable,
        "reach": reach,
    }
'''
src2 = "".join(lines[:start]) + new + "".join(lines[end:])
p.write_text(src2)
print("    OK: patched generated mesh.py")
PY
fi

echo "[8] patch rubik.scramble if needed"
python3 - <<'PY'
import re
from pathlib import Path
p = Path("app/puzzles/rubik.py")
src = p.read_text()
if "produced SOLVED" in src and "for _ in range(64)" in src:
    print("    SKIP: rubik already patched")
    raise SystemExit(0)
pattern = re.compile(r"^def scramble\([^\n]*\n(?:.*\n)*?(?=^def |^class |\Z)", re.MULTILINE)
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
if pattern.search(src):
    p.write_text(pattern.sub(new, src, count=1))
    print("    OK: rubik.scramble patched")
else:
    print("    WARN: scramble() block not matched")
PY

echo "[9] smoke test"
python3 - <<'PY'
from app.train.core import TrainConfig, Trainer
from app.train.mesh import trans
from app.puzzles.rubik import scramble, SOLVED

cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0)
tr = Trainer(cfg)
runs = [tr.run_once(index=i) for i in range(4)]
out = trans(runs)
print("    keys:", out["keys"])
print("    edges:", out["edges"], "pairs:", out["transitive_pairs"])
assert "keys" in out, list(out.keys())
assert out["keys"] == ["r", "r.1", "r.2", "r.1.1"], out["keys"]
assert out["edges"] == 4, out
assert out["transitive_pairs"] == 4, out
for k, v in out["reach"].items():
    assert isinstance(v, list), (k, type(v))
for d in (2, 4, 6, 8):
    assert scramble(n_moves=d, seed=42) != SOLVED, d
print("    OK: smoke test passed")
PY

echo "[10] CLI"
python3 -m app.train.cli 2>&1 | tail -8
