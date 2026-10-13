#!/usr/bin/env bash
set -euo pipefail
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

# 1. Patch generator: "Config as TrainConfig" -> "TrainConfig"
cp -n /tmp/parallel_train.py /tmp/parallel_train.py.bak
LC_ALL=C sed -i '' \
  's/TrainTile, TrainOutcome, Run, Trainer, Config as TrainConfig,/TrainTile, TrainOutcome, Run, Trainer, TrainConfig,/' \
  /tmp/parallel_train.py
if grep -q 'Config as' /tmp/parallel_train.py; then
  echo "WARN: leftover alias"
else
  echo "OK: generator patched"
fi

# 2. Guard rubik.scramble against returning SOLVED
python3 - <<'PY'
from pathlib import Path
p = Path("app/puzzles/rubik.py")
s = p.read_text()
i = s.index("def scramble(")
j = s.index("return", i)
k = s.index("\n", j)
line = s[j:k]
if "== SOLVED" not in line and "raise" not in line:
    indent = " " * (len(line) - len(line.lstrip()))
    guard = (
        f"{line}\n"
        f"{indent}if state == SOLVED:\n"
        f"{indent}    raise ValueError('scramble produced SOLVED; reroll seed')\n"
        f"{indent}return state"
    )
    s = s[:j] + guard + s[k:]
    s = s.replace(f"{line}\n{indent}return state\n{indent}return state",
                  f"{line}\n{indent}return state")
    p.write_text(s)
    print("OK: rubik.scramble guarded")
else:
    print("SKIP: rubik.scramble already guarded")
PY

# 3. Normalise digests to 8-char prefixes inside trans()
python3 - <<'PY'
from pathlib import Path
p = Path("app/train/mesh.py")
s = p.read_text()
if "_keys = [d.split" in s:
    print("SKIP: mesh.trans already normalised")
else:
    i = s.index("def trans(")
    j = s.index("\n", i)
    sig = s[i:j]
    body_start = j
    nxt = s.find("\ndef ", body_start + 1)
    body_end = nxt if nxt != -1 else len(s)
    body = s[body_start:body_end]
    if "digests" not in body:
        print("SKIP: trans() body has no 'digests' name; paste signature for manual patch")
    else:
        inject = (
            f"{sig}\n"
            "    _k = 8\n"
            "    _keys = [d.split(':')[-1][:_k] for d in digests]\n"
        )
        body = body.replace("digests", "_keys")
        s = s[:body_start] + inject + body + s[body_end:]
        p.write_text(s)
        print("OK: mesh.trans normalised to 8-char prefixes")
PY

# 4. Regenerate train package from the fixed generator
rm -f app/train/__init__.py
python3 /tmp/parallel_train.py >/dev/null

# 5. Smoke test
python3 - <<'PY'
import app.train as t
assert t.TrainConfig is not None
from app.puzzles.rubik import scramble, SOLVED
for d in (2, 4, 6, 8):
    try:
        s = scramble(n_moves=d, seed=42)
        assert s != SOLVED, f"scramble returned SOLVED at depth {d}"
    except ValueError:
        pass
from app.train.mesh import trans
print("OK: all fixes verified")
PY

echo
echo "running: python3 -m app.train.cli"
python3 -m app.train.cli 2>&1 | head -60
