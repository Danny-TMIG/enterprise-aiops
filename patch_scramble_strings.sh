#!/usr/bin/env bash
cd ~/enterprise_aiops

python3 - <<'PY'
from pathlib import Path

BROKEN = '''def scramble(n_moves: int = 11, seed: int = 0) -> Tuple[int, ...]:
    rng = random.Random(seed)
    s = SOLVED
    for _ in range(n_moves):
        m = rng.choice(list(MOVES.keys()))
        s = apply_move(MOVES[m], s)
    return s
'''

FIXED = '''def scramble(n_moves: int = 11, seed: int = 0) -> Tuple[int, ...]:
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

for path in ["/tmp/fix_rubik.py", "/tmp/fix_both.py"]:
    p = Path(path)
    if not p.exists():
        print(f"SKIP: {path} missing")
        continue
    src = p.read_text()
    n = src.count(BROKEN)
    if n == 0:
        print(f"WARN: {path} broken block not found "
              f"(already patched? or different template)")
        continue
    src = src.replace(BROKEN, FIXED)
    p.write_text(src)
    print(f"OK: {path} replaced {n} block(s)")
PY

echo
echo "=== regenerate rubik.py from patched generators ==="
for GEN in /tmp/fix_rubik.py /tmp/fix_both.py; do
  [ -f "$GEN" ] || continue
  echo "--- running $GEN ---"
  python3 "$GEN" 2>&1 | tail -5
done

echo
echo "=== verify rubik.py is safe ==="
python3 - <<'PY'
from app.puzzles.rubik import scramble, SOLVED, solve_cube, MOVES, apply_move
for d in (2, 4, 6, 8, 10, 11):
    s = scramble(n_moves=d, seed=42)
    assert s != SOLVED, f"depth {d} returned SOLVED"
    print(f"depth {d:2d}: scrambled ok")

for d in (4, 6, 8, 10):
    s = scramble(n_moves=d, seed=42)
    r = solve_cube(s)
    assert r["solved"]
    cur = s
    for move in r.get("solution", []):
        cur = apply_move(MOVES[move], cur)
    assert cur == SOLVED, f"depth {d} replay failed"
    print(f"depth {d:2d}: solved via {len(r['solution'])} moves, replay OK")

print("OK: rubik.py permanently fixed in the generator")
PY
