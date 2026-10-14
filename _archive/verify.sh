#!/usr/bin/env bash
set -euo pipefail
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

echo "=== 1. generator /tmp/parallel_train.py ==="
if grep -q 'Config as TrainConfig' /tmp/parallel_train.py; then
  cp -n /tmp/parallel_train.py /tmp/parallel_train.py.bak
  LC_ALL=C sed -i '' \
    's/TrainTile, TrainOutcome, Run, Trainer, Config as TrainConfig,/TrainTile, TrainOutcome, Run, Trainer, TrainConfig,/' \
    /tmp/parallel_train.py
  grep -q 'Config as TrainConfig' /tmp/parallel_train.py && { echo "FAIL: alias still present"; exit 1; }
  echo "OK: generator patched"
else
  echo "OK: generator clean"
fi

echo
echo "=== 2. app/train/__init__.py ==="
grep -n 'TrainConfig' app/train/__init__.py

echo
echo "=== 3. rubik.scramble guard ==="
python3 - <<'PY'
from app.puzzles.rubik import scramble, SOLVED
for d in (2, 4, 6, 8, 10):
    try:
        s = scramble(n_moves=d, seed=42)
        if s == SOLVED:
            raise SystemExit(f"FAIL: scramble returned SOLVED at depth {d}")
    except ValueError:
        pass
print("OK: rubik.scramble safe")
PY

echo
echo "=== 4. TrainConfig constructor with REAL fields ==="
python3 - <<'PY'
from app.train.core import TrainConfig, Trainer
from app.train.mesh import trans

print("fields:", list(TrainConfig.__dataclass_fields__.keys()))

cfg = TrainConfig(
    kinds=["sudoku", "tictactoe"],
    difficulties=["easy"],
    puzzles_per_tile=2,
    seed=0,
)
tr = Trainer(cfg)
r1 = tr.run_once(index=0)
r2 = tr.run_once(index=1)
out = trans([r1, r2])
print("run1:", r1.digest)
print("run2:", r2.digest)
print("trans edges:", out["edges"], "pairs:", out["transitive_pairs"])
PY

echo
echo "=== 5. CLI ==="
python3 -m app.train.cli 2>&1 | tail -30
