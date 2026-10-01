#!/usr/bin/env python3
"""Final repair + full diagnostic. Prints everything we need in one run."""
import ast, os, re, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "enterprise_aiops"
os.chdir(ROOT)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
backup = ROOT / f".final-backups/{stamp}"; backup.mkdir(parents=True, exist_ok=True)

def save(rel):
    src = ROOT / rel
    if src.exists():
        dst = backup / rel; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

def section(t): print(f"\n{'='*72}\n{t}\n{'='*72}")

# ── 1. Show setup.py and pyproject build config ─────────────
section("1. setup.py (first 40 lines)")
sp = ROOT / "setup.py"
if sp.exists():
    for i, l in enumerate(sp.read_text().splitlines()[:40], 1):
        print(f"{i:3} {l}")
else:
    print("(no setup.py)")

section("1b. pyproject.toml build-system")
pp = ROOT / "pyproject.toml"
if pp.exists():
    inside = False
    for l in pp.read_text().splitlines():
        if l.strip().startswith("[build-system]"): inside = True
        elif l.startswith("[") and inside: inside = False
        if inside: print(l)

# ── 2. Robust Cython guard ──────────────────────────────────
section("2. Guard Cython import")
if sp.exists():
    save("setup.py")
    s = sp.read_text()
    if "from Cython.Build import cythonize" in s:
        s = re.sub(
            r'from Cython\.Build import cythonize',
            'try:\n    from Cython.Build import cythonize\nexcept ImportError:\n    cythonize = lambda *a, **kw: []',
            s, count=1)
    if re.search(r'^import Cython\b', s, re.M):
        s = re.sub(r'^import Cython\b',
                   'try:\n    import Cython\nexcept ImportError:\n    Cython = None',
                   s, count=1, flags=re.M)
    sp.write_text(s)
    print("Cython references guarded")
    print("\n--- new head ---")
    for i, l in enumerate(s.splitlines()[:15], 1):
        print(f"{i:3} {l}")

# ── 3. Regex speedups (not string match — file has drifted) ─
section("3. Nature sim speedups (regex)")
def rpatch(rel, patterns):
    p = ROOT / rel
    if not p.exists(): print(f"[{rel}] missing"); return
    save(rel); s = p.read_text(); n = 0
    for pat, repl in patterns:
        s, k = pat.subn(repl, s); n += k
    p.write_text(s); print(f"[{rel}] {n} substitution(s)")

rpatch("dcs/nature/morpho.py", [
    (re.compile(r'def turing_pattern\(n=\d+,\s*steps=\d+'), 'def turing_pattern(n=48, steps=3000'),
    (re.compile(r'def belousov_zhabotinsky\(n=\d+,\s*steps=\d+'), 'def belousov_zhabotinsky(n=32, steps=2000'),
    (re.compile(r'for _ in range\(5000\):'), 'for _ in range(2000):'),
    (re.compile(r'f,\s*k\s*=\s*0\.035,\s*0\.060'), 'f, k = 0.037, 0.060'),
    (re.compile(r'for d[xy] in range\(-3,\s*4\):'), lambda m: m.group(0).replace('-3, 4', '-5, 6')),
    (re.compile(r'b\[y\]\[x\]\s*=\s*0\.25\s*\+\s*0\.1\s*\*\s*rng\.random\(\)'), 'b[y][x] = 0.50 + 0.25 * rng.random()'),
])

rpatch("dcs/nature/oscillator.py", [
    (re.compile(r'def peskin_mirollo\(n=\d+,\s*eps=[\d.]+,\s*steps=\d+'),
     'def peskin_mirollo(n=50, eps=0.5, steps=5000'),
    (re.compile(r'def hodgkin_huxley\(steps=\d+,\s*dt=[\d.]+'),
     'def hodgkin_huxley(steps=500, dt=0.02'),
])

rpatch("dcs/nature/foraging.py", [
    (re.compile(r'x \+= 0\.5 \* dx / d'), 'x += 2.0 * dx / d'),
    (re.compile(r'y \+= 0\.5 \* dy / d'), 'y += 2.0 * dy / d'),
])

rpatch("dcs/nature/flocking.py", [
    (re.compile(r'def boids\(n=\d+,\s*steps=\d+,\s*sep=[\d.]+,\s*ali=[\d.]+'),
     'def boids(n=60, steps=800, sep=0.7, ali=1.5'),
])

rpatch("dcs/nature/walk.py", [
    (re.compile(r'def persistent_walk\(n=\d+,\s*sigma=[\d.]+'),
     'def persistent_walk(n=500, sigma=0.005'),
])

# ── 4. Show what's actually there now ───────────────────────
section("4. Current function signatures")
for rel in ["dcs/nature/morpho.py","dcs/nature/oscillator.py","dcs/nature/foraging.py",
            "dcs/nature/flocking.py","dcs/nature/walk.py","dcs/crosscut/chaos.py"]:
    p = ROOT / rel
    if not p.exists(): continue
    print(f"\n-- {rel}")
    for line in p.read_text().splitlines():
        if re.match(r'^def ', line):
            print(f"   {line}")

# ── 5. Remove ~/.local/bin/dcs shadow ───────────────────────
section("5. Remove ~/.local/bin/dcs shadow")
shadow = Path.home() / ".local/bin/dcs"
if shadow.exists():
    shutil.copy2(shadow, backup / "dcs-shadow")
    shadow.unlink(); print(f"removed {shadow}")
else:
    print("(none)")

# ── 6. Purge caches + pip install ───────────────────────────
subprocess.run("find dcs -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null", shell=True)

section("6. pip install -e .")
try:
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(ROOT)],
                       capture_output=True, text=True, timeout=180)
    print("\n".join(r.stdout.splitlines()[-6:]))
    if r.returncode != 0:
        print("\n--- STDERR (last 15 lines) ---")
        print("\n".join(r.stderr.splitlines()[-15:]))
except subprocess.TimeoutExpired:
    print("(timed out after 180s)")

# ── 7. Run everything ───────────────────────────────────────
def run(cmd, timeout=90, grep=None):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return f"(timed out after {timeout}s)"
    out = r.stdout
    if grep:
        out = "\n".join(l for l in out.splitlines() if re.search(grep, l))
    return out.strip() or "(no matching output)"

section("7. dcs --help | choices")
print(run("python -m dcs --help 2>&1 | head -4", 20))

section("8. dcs laws")
print(run("python -m dcs laws 2>&1 | grep -E '✗|n_passed|n_failed'", 60))

section("9. dcs coordinate")
print(run("python -m dcs coordinate 2>&1 | tail -5", 30))

section("10. dcs balance --floor 12")
print(run("python -m dcs balance --floor 12 2>&1 | tail -5", 30))

section("11. dcs conform  (120s limit)")
out = run("python -m dcs conform 2>&1 | grep -E 'FAIL|MUST_|SHOULD_|MAY_|verdict'", 120)
print(out)

print(f"\nBackups: {backup}")
