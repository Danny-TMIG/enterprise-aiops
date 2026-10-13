#!/usr/bin/env bash
# Parallel version: patches, regenerates, and verifies puzzle generators
# concurrently, then runs the full train pipeline.
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

GENS=(/tmp/fix_rubik.py /tmp/fix_both.py)
LOG_DIR=/tmp/puzzle_gen_logs
rm -rf "$LOG_DIR"; mkdir -p "$LOG_DIR"

echo "[1] restore any .DISABLED markers (parallel)"
PIDS=()
for GEN in "${GENS[@]}"; do
  (
    if [ -f "${GEN}.DISABLED" ] && [ ! -f "$GEN" ]; then
      mv "${GEN}.DISABLED" "$GEN"
      echo "    unmarked ${GEN}.DISABLED"
    elif [ -f "$GEN" ]; then
      echo "    ${GEN} already enabled"
    else
      echo "    ${GEN} not present"
    fi
  ) > "$LOG_DIR/restore.$(basename "$GEN").log" 2>&1 &
  PIDS+=($!)
done
for pid in "${PIDS[@]}"; do wait "$pid" || true; done
cat "$LOG_DIR"/restore.*.log

echo
echo "[2] patch embedded templates (parallel)"
PIDS=()
for GEN in "${GENS[@]}"; do
  (
    python3 - "$GEN" <<'PY'
import ast, sys
from pathlib import Path

gen_path = Path(sys.argv[1])
if not gen_path.exists():
    print(f"    SKIP: {gen_path}")
    raise SystemExit(0)

src = gen_path.read_text()

FIXES = [
    # A) _inv_move helper after apply_move
    (
        'def apply_move(sigma: Tuple[int, ...], state: Tuple[int, ...]\n'
        '               ) -> Tuple[int, ...]:\n'
        '    return tuple(state[sigma[i]] for i in range(8))\n',
        'def apply_move(sigma: Tuple[int, ...], state: Tuple[int, ...]\n'
        '               ) -> Tuple[int, ...]:\n'
        '    return tuple(state[sigma[i]] for i in range(8))\n'
        '\n'
        '\n'
        'def _inv_move(name: str) -> str:\n'
        "    \"\"\"Name of the inverse move.\"\"\"\n"
        "    if name.endswith(\"'\"):\n"
        '        return name[:-1]\n'
        '    if name.endswith("2"):\n'
        '        return name\n'
        "    return name + \"'\"\n",
    ),
    # B) guarded scramble
    (
        'def scramble(n_moves: int = 11, seed: int = 0) -> Tuple[int, ...]:\n'
        '    rng = random.Random(seed)\n'
        '    s = SOLVED\n'
        '    for _ in range(n_moves):\n'
        '        m = rng.choice(list(MOVES.keys()))\n'
        '        s = apply_move(MOVES[m], s)\n'
        '    return s\n',
        'def scramble(n_moves: int = 11, seed: int = 0) -> Tuple[int, ...]:\n'
        '    rng = random.Random(seed)\n'
        '    for _ in range(64):\n'
        '        s = SOLVED\n'
        '        for _ in range(n_moves):\n'
        '            m = rng.choice(list(MOVES.keys()))\n'
        '            s = apply_move(MOVES[m], s)\n'
        '        if s != SOLVED:\n'
        '            return s\n'
        '    raise ValueError("scramble could not escape SOLVED in 64 attempts")\n',
    ),
    # C) fix solve_cube direction
    (
        '        prev, move = parent[cur]\n'
        '        path.append(move)\n'
        '        cur = prev\n'
        '    path.reverse()\n',
        '        prev, move = parent[cur]\n'
        '        path.append(_inv_move(move))\n'
        '        cur = prev\n',
    ),
]

counts = []
for old, new in FIXES:
    n = src.count(old)
    if n:
        src = src.replace(old, new)
    counts.append(n)

ast.parse(src)
gen_path.write_text(src)
print(f"    {gen_path}: A={counts[0]} B={counts[1]} C={counts[2]}, parses OK")
PY
  ) > "$LOG_DIR/patch.$(basename "$GEN").log" 2>&1 &
  PIDS+=($!)
done
for pid in "${PIDS[@]}"; do wait "$pid" || true; done
cat "$LOG_DIR"/patch.*.log

echo
echo "[3] run generators (parallel)"
PIDS=()
for GEN in "${GENS[@]}"; do
  [ -f "$GEN" ] || continue
  (
    python3 "$GEN" 2>&1 | tail -5
  ) > "$LOG_DIR/run.$(basename "$GEN").log" 2>&1 &
  PIDS+=($!)
done
for pid in "${PIDS[@]}"; do wait "$pid" || true; done
cat "$LOG_DIR"/run.*.log

echo
echo "[4] verify emitted rubik.py"
python3 - <<'PY'
from app.puzzles.rubik import RubikCube, scramble, solve_cube, SOLVED, MOVES, apply_move

ok = True
for d in (2, 4, 6, 8, 10, 11):
    s = scramble(n_moves=d, seed=42)
    if s == SOLVED:
        print(f"    FAIL depth {d}: scramble returned SOLVED"); ok = False; continue
    r = solve_cube(s)
    if not r["solved"]:
        print(f"    FAIL depth {d}: solve_cube failed"); ok = False; continue
    cur = s
    for m in r["solution"]:
        cur = apply_move(MOVES[m], cur)
    if cur != SOLVED:
        print(f"    FAIL depth {d}: replay failed (len={len(r['solution'])})"); ok = False
    else:
        print(f"    OK depth {d:2d}: {len(r['solution'])} moves, replay OK")

if not ok:
    raise SystemExit("    verification failed")
print("    OK: rubik.py verified")
PY
VERIFY_RC=$?

if [ "$VERIFY_RC" -ne 0 ]; then
  echo "[!] verification failed — re-disabling generators"
  for GEN in "${GENS[@]}"; do
    [ -f "$GEN" ] && mv "$GEN" "$GEN.DISABLED"
  done
  exit 1
fi

echo
echo "[5] confirm parallel_train.py does not clobber rubik.py"
grep -n "rubik" /tmp/parallel_train.py | grep -E "write_text|FILES|open\(" \
  && echo "    WARN: clobber risk" \
  || echo "    no write_text for rubik.py — safe"

echo
echo "[6] regenerate app/train/ in parallel with nothing else (it owns app/train/)"
python3 /tmp/parallel_train.py > "$LOG_DIR/train_regen.log" 2>&1 &
TRAIN_PID=$!
wait "$TRAIN_PID" || { echo "    FAIL: parallel_train.py"; tail "$LOG_DIR/train_regen.log"; exit 1; }
tail -12 "$LOG_DIR/train_regen.log"

echo
echo "[7] full pipeline"
python3 -m app.train.cli 2>&1 | tail -6

echo
echo "[8] combined green check"
python3 - <<'PY'
from app.puzzles.rubik import RubikCube, scramble, solve_cube, SOLVED, MOVES, apply_move
from app.train.core import TrainConfig, Trainer
from app.train.mesh import trans

for d in (2, 4, 6, 8, 10, 11):
    s = scramble(n_moves=d, seed=42); assert s != SOLVED, d
    r = solve_cube(s); assert r["solved"], d
    cur = s
    for m in r["solution"]: cur = apply_move(MOVES[m], cur)
    assert cur == SOLVED, d

cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0)
runs = [Trainer(cfg).run_once(index=i) for i in range(4)]
out = trans(runs)
assert out["keys"] == ["r", "r.1", "r.2", "r.1.1"], out
assert out["edges"] == 4 and out["transitive_pairs"] == 4, out
print("ALL GREEN")
PY
