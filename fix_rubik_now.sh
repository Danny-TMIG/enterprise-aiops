#!/usr/bin/env bash
set -euo pipefail
cd ~/enterprise_aiops

echo "=== backup ==="
cp app/puzzles/rubik.py app/puzzles/rubik.py.bak.$(date +%s)

echo "=== show lines 55-90 of current file ==="
sed -n '55,90p' app/puzzles/rubik.py

echo
echo "=== strip every 'produced SOLVED' guard and adjacent stray lines ==="
python3 - <<'PY'
from pathlib import Path

p = Path("app/puzzles/rubik.py")
lines = p.read_text().splitlines(keepends=True)

out = []
i = 0
while i < len(lines):
    raw = lines[i]
    s = raw.strip()

    # 1. any line mentioning the injected message
    if "produced SOLVED" in s:
        i += 1
        continue

    # 2. any line that is exactly "if state == SOLVED:" that is immediately
    #    followed (allowing blanks) by a raise/return referencing SOLVED
    if s == "if state == SOLVED:":
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1
        if j < len(lines):
            nxt = lines[j].strip()
            if ("raise" in nxt or "return" in nxt) and "SOLVED" in nxt:
                i = j + 1
                continue

    # 3. any line that is exactly "return state" preceded by a blank line
    #    and with zero indentation, but inside a class body — rare, skip

    out.append(raw)
    i += 1

src = "".join(out)

# 4. also collapse duplicate consecutive "return state" lines
lines2 = src.splitlines(keepends=True)
dedup = []
prev_was_return = False
for ln in lines2:
    if ln.strip() == "return state":
        if prev_was_return:
            continue
        prev_was_return = True
    else:
        prev_was_return = False
    dedup.append(ln)
src = "".join(dedup)

try:
    compile(src, str(p), "exec")
    p.write_text(src)
    print("OK: rubik.py compiles")
except SyntaxError as e:
    print(f"still broken: {e}")
    ctx = src.splitlines()
    lo = max(0, (e.lineno or 1) - 8)
    hi = min(len(ctx), (e.lineno or 1) + 8)
    for n in range(lo, hi):
        mark = ">>" if n + 1 == e.lineno else "  "
        print(f"{mark} {n+1:4d}: {ctx[n]}")
    raise SystemExit(1)
PY

echo
echo "=== smoke test rubik ==="
python3 - <<'PY'
from app.puzzles.rubik import scramble, SOLVED
for d in (2, 4, 6, 8):
    try:
        s = scramble(n_moves=d, seed=42)
        assert s != SOLVED, f"SOLVED at depth {d}"
        print(f"depth {d}: ok")
    except ValueError:
        print(f"depth {d}: scrambled to SOLVED, guard raised (ok)")
PY
