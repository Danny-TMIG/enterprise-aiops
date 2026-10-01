#!/usr/bin/env bash
# Idempotent: patches .DISABLED puzzle generators, re-enables them,
# runs them, verifies the emitted rubik.py, and rolls back on failure.
# Safe to re-run.
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

echo "[1] find disabled generators"
FOUND=0
for GEN in /tmp/fix_rubik.py /tmp/fix_both.py; do
  if [ -f "${GEN}.DISABLED" ]; then
    echo "    ${GEN}.DISABLED present"
    FOUND=1
  elif [ -f "$GEN" ]; then
    echo "    ${GEN} already enabled"
    FOUND=1
  else
    echo "    ${GEN} not present (skip)"
  fi
done
[ "$FOUND" = "1" ] || { echo "    no puzzle generators found"; exit 0; }

echo "[2] patch embedded templates (idempotent)"
python3 - <<'PY'
from pathlib import Path

# Correct replacements for the template strings inside each generator.
FIXES = [
    # A) insert _inv_move helper right after apply_move
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
    # B) guard scramble
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
    # C) fix solve_cube parent-walk direction (no reversal needed)
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

for gen_name in ("/tmp/fix_rubik.py", "/tmp/fix_both.py"):
    src_path = Path(gen_name)
    dis_path = Path(gen_name + ".DISABLED")
    if dis_path.exists() and not src_path.exists():
        src_path.write_text(dis_path.read_text())
    if not src_path.exists():
        print(f"    SKIP: {gen_name}")
        continue

    src = src_path.read_text()
    hits = []
    for i, (old, new) in enumerate(FIXES):
        n = src.count(old)
        if n:
            src = src.replace(old, new)
        hits.append(n)
    src_path.write_text(src)
    print(f"    {gen_name}: fixes applied A={hits[0]} B={hits[1]} C={hits[2]}")

    # syntax check
    import ast
    ast.parse(src)
    print(f"    {gen_name}: parses OK")
PY

echo "[3] re-enable (remove .DISABLED marker)"
for GEN in /tmp/fix_rubik.py /tmp/fix_both.py; do
  [ -f "${GEN}.DISABLED" ] && mv "${GEN}.DISABLED" "${GEN}.DISABLED.bak" \
    && echo "    unmarked ${GEN}.DISABLED"
done

echo "[4] run generators"
python3 /tmp/fix_rubik.py 2>&1 | tail -3
python3 /tmp/fix_both.py  2>&1 | tail -3

echo "[5] verify emitted rubik.py"
python3 - <<'PY'
from app.puzzles.rubik import RubikCube, scramble, solve_cube, SOLVED, MOVES, apply_move

ok = True
for d in (2, 4, 6, 8, 10, 11):
    s = scramble(n_moves=d, seed=42)
    if s == SOLVED:
        print(f"    FAIL depth {d}: scramble returned SOLVED")
        ok = False
        continue
    r = solve_cube(s)
    if not r["solved"]:
        print(f"    FAIL depth {d}: solve_cube failed")
        ok = False
        continue
    cur = s
    for move in r["solution"]:
        cur = apply_move(MOVES[move], cur)
    if cur != SOLVED:
        print(f"    FAIL depth {d}: replay failed (len={len(r['solution'])})")
        ok = False
    else:
        print(f"    OK depth {d:2d}: {len(r['solution'])} moves, replay OK")

if not ok:
    raise SystemExit("    verification failed")
print("    OK: rubik.py verified")
PY

if [ $? -ne 0 ]; then
  echo "[!] verification failed — re-disabling generators"
  for GEN in /tmp/fix_rubik.py /tmp/fix_both.py; do
    [ -f "$GEN" ] && mv "$GEN" "$GEN.DISABLED"
    [ -f "${GEN}.DISABLED.bak" ] && rm -f "${GEN}.DISABLED.bak"
  done
  exit 1
fi

echo "[6] clean .bak markers"
rm -f /tmp/fix_rubik.py.DISABLED.bak /tmp/fix_both.py.DISABLED.bak

echo "[7] confirm parallel_train.py does not clobber rubik.py"
grep -n "rubik" /tmp/parallel_train.py | grep -E "write_text|FILES|open\(" || echo "    no write_text for rubik.py — safe"

echo "[8] full pipeline"
python3 -m app.train.cli 2>&1 | tail -6
