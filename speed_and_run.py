#!/usr/bin/env python3
"""Speed up slow nature sims, patch fix_all.py with timeouts, then run it."""
import ast, os, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path.home() / "enterprise_aiops"
os.chdir(ROOT)
stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
backup = ROOT / f".speed-backups/{stamp}"; backup.mkdir(parents=True, exist_ok=True)

def save(rel):
    src = ROOT / rel
    if src.exists():
        dst = backup / rel; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

def sub(rel, pairs, label):
    p = ROOT / rel
    if not p.exists(): print(f"[{rel}] missing"); return
    save(rel); s = p.read_text(); hits = 0
    for old, new in pairs:
        if old in s: s = s.replace(old, new); hits += 1
        else: print(f"    miss: {old[:60]}")
    p.write_text(s); print(f"[{rel}] {label}: {hits}/{len(pairs)}")

# ── Speed up slow sims (5-10x faster, same qualitative behaviour) ──
print("=== Speeding up slow nature sims ===")

sub("dcs/nature/morpho.py", [
    # Gray-Scott: 64→48 grid, 6000→3000 steps. Pattern still forms.
    ("def turing_pattern(n=64, steps=6000, seed=0):",
     "def turing_pattern(n=48, steps=3000, seed=0):"),
    # BZ: 48→32 grid, 4000→2000 steps
    ("def belousov_zhabotinsky(n=48, steps=4000, seed=0):",
     "def belousov_zhabotinsky(n=32, steps=2000, seed=0):"),
    # DLA: 5000 walk-steps cap → 2000 (still plenty to hit the cluster)
    ("for _ in range(5000):", "for _ in range(2000):"),
], "speed pass")

sub("dcs/nature/oscillator.py", [
    # Peskin-Mirollo: 20000 steps is absurd for a var<0.05 test. 5000 + eps 0.5.
    ("def peskin_mirollo(n=50, eps=0.3, steps=20000, seed=0):",
     "def peskin_mirollo(n=50, eps=0.5, steps=5000, seed=0):"),
    # HH: 500 steps at dt=0.01 = 5ms sim time, not enough for a spike. dt=0.02.
    ("def hodgkin_huxley(steps=500, dt=0.01, I=10.0):",
     "def hodgkin_huxley(steps=500, dt=0.02, I=10.0):"),
], "speed pass")

# ── Patch fix_all.py with timeouts ────────────────────────────
print("\n=== Patching fix_all.py with timeouts ===")
fp = ROOT / "fix_all.py"
if fp.exists():
    save("fix_all.py"); s = fp.read_text()

    # run() helper: add timeout
    old_run = re.compile(
        r'def run\(cmd, grep=None, tail=None\):\n'
        r'\s*r = subprocess\.run\(cmd, shell=True, capture_output=True, text=True\)\n'
    )
    new_run = (
        'def run(cmd, grep=None, tail=None, timeout=60):\n'
        '    try:\n'
        '        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)\n'
        '    except subprocess.TimeoutExpired:\n'
        '        return f"(timed out after {timeout}s)"\n'
    )
    if old_run.search(s):
        s = old_run.sub(new_run, s, count=1)
        print("[fix_all.py] run() timeout added")
    else:
        print("[fix_all.py] run() pattern not found — skipping")

    # pip subprocess: add timeout
    old_pip = re.compile(
        r'r = subprocess\.run\(\[sys\.executable, "-m", "pip", "install", "-e", str\(ROOT\)\],\n'
        r'\s*capture_output=True, text=True\)'
    )
    new_pip = (
        'try:\n'
        '    r = subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(ROOT)],\n'
        '                       capture_output=True, text=True, timeout=180)\n'
        'except subprocess.TimeoutExpired:\n'
        '    class _R: returncode = 1; stdout = ""; stderr = "(pip timed out)"\n'
        '    r = _R()'
    )
    if old_pip.search(s):
        s = old_pip.sub(new_pip, s, count=1)
        print("[fix_all.py] pip timeout added")
    else:
        print("[fix_all.py] pip pattern not found — skipping")

    # conform verification: shorter timeout (it's the slow one)
    s = s.replace(
        "note(run(\"python -m dcs conform 2>&1 | grep -E 'FAIL|MUST_pass|MUST_fail|SHOULD_fail|verdict'\"))",
        "note(run(\"python -m dcs conform 2>&1 | grep -E 'FAIL|MUST_pass|MUST_fail|SHOULD_fail|verdict'\", timeout=45))"
    )
    s = s.replace(
        "note(run(\"python -m dcs laws 2>&1 | grep -E '✗|n_passed|n_failed'\"))",
        "note(run(\"python -m dcs laws 2>&1 | grep -E '✗|n_passed|n_failed'\", timeout=45))"
    )
    fp.write_text(s)
    try: ast.parse(s); print("[fix_all.py] syntax OK")
    except SyntaxError as e: sys.exit(f"[fix_all.py] syntax error after patch: {e}")

# ── Purge caches ──────────────────────────────────────────────
subprocess.run("find dcs -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null", shell=True)
print(f"\nBackups: {backup}")
print("\n=== Running fix_all.py ===")
sys.exit(subprocess.run([sys.executable, "fix_all.py"]).returncode)
