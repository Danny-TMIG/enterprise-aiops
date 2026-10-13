"""Normalize app/train/cli.py's pollinate print loop.

The generator emits a version that does `p['kind']` etc, which crashes
because pollinate() returns {stream, change, a, b, delta}. This replaces
just that loop with a defensive version. Idempotent.
"""
import ast
import re
from pathlib import Path

p = Path("app/train/cli.py")
src = p.read_text()

# If cli.py already uses .get on stream, we're fine.
if 'p.get("stream")' in src or "p.get('stream')" in src:
    print("cli.py: already fixed")
    raise SystemExit(0)

# Find the pollinate print block: `for p in pl[:12]:` or `for p in pl:`
pattern = re.compile(
    r"(    for p in pl(?:\[[^\]]*\])?:\n)"
    r"((?:        .*\n)+)"
)

new_loop = '''    for p in pl[:12]:
        parts = (p.get("stream") or "").split("/")
        kind = parts[0] if len(parts) > 0 else p.get("kind", "?")
        solver = parts[1] if len(parts) > 1 else p.get("solver", "?")
        difficulty = parts[2] if len(parts) > 2 else p.get("difficulty", "?")
        a = p.get("a")
        b = p.get("b")
        delta = p.get("delta") or 0.0
        change = p.get("change", "changed")
        if change == "added":
            print(f"    {kind:10s} {difficulty:6s}  {solver:8s}  - -> +  b={b}")
        elif change == "removed":
            print(f"    {kind:10s} {difficulty:6s}  {solver:8s}  + -> -  a={a}")
        else:
            a_s = f"{a:.2f}" if isinstance(a, (int, float)) else str(a)
            b_s = f"{b:.2f}" if isinstance(b, (int, float)) else str(b)
            print(f"    {kind:10s} {difficulty:6s}  {solver:8s}  "
                  f"{a_s} -> {b_s}  delta={delta:+.3f}")
'''

if not pattern.search(src):
    print("cli.py: pollinate loop not found — skipping")
    raise SystemExit(0)

src = pattern.sub(new_loop, src, count=1)
ast.parse(src)
p.write_text(src)
print("cli.py: pollinate print loop replaced")
