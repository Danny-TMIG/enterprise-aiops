#!/usr/bin/env bash
cd ~/enterprise_aiops

NEW_BLOCK='def scramble(n_moves: int = 11, seed: int = 0) -> Tuple[int, ...]:
    rng = random.Random(seed)
    for _ in range(64):
        s = SOLVED
        for _ in range(n_moves):
            m = rng.choice(list(MOVES.keys()))
            s = apply_move(MOVES[m], s)
        if s != SOLVED:
            return s
    raise ValueError("scramble could not escape SOLVED in 64 attempts")'

for GEN in /tmp/fix_both.py /tmp/fix_rubik.py; do
  [ -f "$GEN" ] || { echo "SKIP: $GEN missing"; continue; }
  echo "=== patching $GEN ==="
  cp -n "$GEN" "${GEN}.bak.$(date +%s)" 2>/dev/null
  GEN="$GEN" NEW_BLOCK="$NEW_BLOCK" python3 - <<'PY'
import ast, os, re
from pathlib import Path

gen = Path(os.environ["GEN"])
new_body = os.environ["NEW_BLOCK"]
src = gen.read_text()

# Match any def scramble(...) up to next top-level def/class/triple-quote/EOF.
pat = re.compile(
    r"(?ms)^def scramble\([^\n]*\n(?:.*\n)*?"
    r"(?=^def |^class |^'''|^\"\"\"|\Z)"
)

m = pat.search(src)
if not m:
    print(f"    no scramble() block found — checking whether it's inside a string template")
    # It may live inside a triple-quoted FILES dict string. Look for the
    # pattern inside embedded python source too.
    inner = re.search(
        r"(?ms)^(\s*)def scramble\([^\n]*\n"
        r"(?:\1.*\n)*?"
        r"(?=\1def |\1class |\1'''|\1\"\"\"|\1\Z|\Z)",
        src,
    )
    if not inner:
        raise SystemExit("    FAIL: no scramble() anywhere")
    indent = inner.group(1)
    indented = "\n".join(
        (indent + ln if ln.strip() else ln) for ln in new_body.splitlines()
    ) + "\n\n"
    src2 = src[:inner.start()] + indented + src[inner.end():]
else:
    src2 = src[:m.start()] + new_body + "\n\n\n" + src[m.end():]

# Try to parse the outer file. If it's a generator that embeds code in a
# string, ast.parse still works because the string content isn't parsed.
try:
    ast.parse(src2)
except SyntaxError as e:
    raise SystemExit(f"    FAIL: patched generator has syntax error: {e}")

gen.write_text(src2)
print(f"    OK: {gen} patched")
PY
done

echo
echo "=== verify generators still executable ==="
for GEN in /tmp/fix_both.py /tmp/fix_rubik.py; do
  [ -f "$GEN" ] || continue
  python3 -c "import ast; ast.parse(open('$GEN').read()); print('    OK: $GEN parses')" \
    || echo "    FAIL: $GEN broken"
done

echo
echo "=== rebake rubik.py from the patched generator and verify ==="
python3 /tmp/fix_rubik.py 2>&1 | tail -5
python3 /tmp/fix_both.py 2>&1 | tail -5

python3 - <<'PY'
from app.puzzles.rubik import scramble, SOLVED
for d in (2, 4, 6, 8):
    assert scramble(n_moves=d, seed=42) != SOLVED, d
print("OK: rubik.scramble safe after regeneration")
PY
