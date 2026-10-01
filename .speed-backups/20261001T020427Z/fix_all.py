#!/usr/bin/env python3
"""One-shot repair. Backs up, fixes everything, verifies, reports."""
import ast, os, re, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path.home() / "enterprise_aiops"
os.chdir(ROOT)
stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
backup = ROOT / f".fix_all-backups/{stamp}"
backup.mkdir(parents=True, exist_ok=True)
log = []
def note(msg):
    print(msg); log.append(msg)

def save(rel):
    src = ROOT / rel
    if src.exists():
        dst = backup / rel; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

# ── 1. setup.py: Cython optional ──────────────────────────────
sp = ROOT / "setup.py"
if sp.exists():
    save("setup.py")
    s = sp.read_text()
    if "from Cython.Build import cythonize" in s and "except ImportError" not in s.split("cythonize")[0][-80:]:
        s = s.replace(
            "from Cython.Build import cythonize",
            "try:\n    from Cython.Build import cythonize\nexcept ImportError:\n    cythonize = None")
        sp.write_text(s); note("[setup.py] Cython optional")
    else:
        note("[setup.py] already patched")

# ── 2. oscillator.py: circadian_clock via regex ───────────────
op = ROOT / "dcs/nature/oscillator.py"
if op.exists():
    save("dcs/nature/oscillator.py")
    s = op.read_text()
    new_fn = '''def circadian_clock(steps=800, delay=15, gain=3.5, dt=0.05):
    """Delayed negative feedback ring buffer; gain*delay*dt > pi/2 yields limit cycle."""
    buf = [0.5] * delay
    x = []
    for i in range(steps):
        prev = x[-1] if x else 0.5
        delayed = buf[i % delay]
        v = prev + dt * (1.0 - gain * delayed)
        v = max(0.0, min(1.5, v))
        buf[i % delay] = v
        x.append(v)
    return x
'''
    pat = re.compile(r'def circadian_clock\([^)]*\):.*?(?=\n(?:def |@|class |\Z))', re.DOTALL)
    if pat.search(s):
        s = pat.sub(new_fn, s, count=1)
        op.write_text(s)
        note("[oscillator.py] circadian_clock rewritten (ring buffer)")
    else:
        note("[oscillator.py] circadian_clock not found — appended")
        op.write_text(s + "\n\n" + new_fn)

# ── 3. morpho.py: Gray-Scott unstable regime ─────────────────
mp = ROOT / "dcs/nature/morpho.py"
if mp.exists():
    save("dcs/nature/morpho.py")
    s = mp.read_text(); hits = 0
    for old, new in [
        ("f, k = 0.035, 0.060", "f, k = 0.037, 0.060"),
        ("for dy in range(-3, 4):", "for dy in range(-5, 6):"),
        ("for dx in range(-3, 4):", "for dx in range(-5, 6):"),
        ("b[y][x] = 0.25 + 0.1 * rng.random()", "b[y][x] = 0.50 + 0.25 * rng.random()"),
    ]:
        if old in s: s = s.replace(old, new); hits += 1
    mp.write_text(s); note(f"[morpho.py] {hits}/4 substitutions")

# ── 4. foraging.py: stronger gradient pull ────────────────────
fp = ROOT / "dcs/nature/foraging.py"
if fp.exists():
    save("dcs/nature/foraging.py")
    s = fp.read_text(); hits = 0
    for old, new in [
        ("x += 0.5 * dx / d", "x += 2.0 * dx / d"),
        ("y += 0.5 * dy / d", "y += 2.0 * dy / d"),
    ]:
        if old in s: s = s.replace(old, new); hits += 1
    fp.write_text(s); note(f"[foraging.py] {hits}/2 substitutions")

# ── 5. flocking.py: boids params ──────────────────────────────
flp = ROOT / "dcs/nature/flocking.py"
if flp.exists():
    save("dcs/nature/flocking.py")
    s = flp.read_text(); hits = 0
    old_sig = "def boids(n=60, steps=400, sep=0.7, ali=0.9, coh=0.4, seed=0):"
    new_sig = "def boids(n=60, steps=800, sep=0.7, ali=1.5, coh=0.4, seed=0):"
    if old_sig in s: s = s.replace(old_sig, new_sig); hits += 1
    flp.write_text(s); note(f"[flocking.py] {hits}/1 substitutions")

# ── 6. walk.py: persistent_walk lower sigma ───────────────────
wp = ROOT / "dcs/nature/walk.py"
if wp.exists():
    save("dcs/nature/walk.py")
    s = wp.read_text(); hits = 0
    old_sig = "def persistent_walk(n=500, sigma=0.02, seed=0):"
    new_sig = "def persistent_walk(n=500, sigma=0.005, seed=0):"
    if old_sig in s: s = s.replace(old_sig, new_sig); hits += 1
    wp.write_text(s); note(f"[walk.py] {hits}/1 substitutions")

# ── 7. laws.py: CHAOS-FRACTION delegates to chaos.test ────────
lp = ROOT / "dcs/laws.py"
if lp.exists():
    save("dcs/laws.py")
    src = lp.read_text()
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        note(f"[laws.py] SYNTAX ERROR: {e}"); tree = None
    if tree is not None:
        target = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for d in node.decorator_list:
                    try: ds = ast.unparse(d)
                    except Exception: ds = ""
                    if "CHAOS-FRACTION" in ds:
                        target = node; break
            if target: break
        if target is None:
            note("[laws.py] CHAOS-FRACTION not found via AST — will append fresh law")
            new_law = '''

try:
    from dcs.generate import requirement as _requirement
except Exception:
    _requirement = None

def _chaos_fraction_law():
    from dcs.crosscut.chaos import test as _t
    _t()

if _requirement is not None:
    try:
        _chaos_fraction_law = _requirement(
            id="CHAOS-FRACTION",
            title="chaos injects configured fraction",
            section="X.chaos", hats=["SRE"], criticality="MUST")(_chaos_fraction_law)
    except Exception:
        pass
'''
            lp.write_text(src + new_law)
            note("[laws.py] appended fresh CHAOS-FRACTION law")
        else:
            lines = src.splitlines(keepends=True)
            dec_start = target.lineno - 1
            if target.decorator_list:
                dec_start = min(d.lineno for d in target.decorator_list) - 1
            decorators = lines[dec_start:target.lineno - 1]
            new_src = ("".join(lines[:dec_start]) + "".join(decorators)
                       + f"def {target.name}(*a, **kw):\n"
                         "    from dcs.crosscut.chaos import test as _t\n    _t()\n"
                       + "".join(lines[target.end_lineno:]))
            try:
                ast.parse(new_src)
                lp.write_text(new_src)
                note(f"[laws.py] {target.name}() delegates to chaos.test()")
            except SyntaxError as e:
                note(f"[laws.py] replacement produced bad syntax: {e}; skipping")

# ── 8. cli.py: wrapper with missing subcommands ──────────────
cli = ROOT / "dcs/cli.py"
orig = ROOT / "dcs/_cli_orig.py"
if cli.exists() and not orig.exists():
    save("dcs/cli.py")
    shutil.copy2(cli, orig)
    wrapper = '''"""CLI entry. Delegates to dcs._cli_orig and adds extra subcommands."""
import argparse, sys
from dcs import _cli_orig

def _coordinate(argv):
    from dcs import team
    fn = getattr(team, "coordinate", None) or getattr(team, "main", None)
    print(fn() if fn else "dcs.team: no entry point")

def _conformance(argv):
    from dcs.tests import conformance as c
    fn = getattr(c, "report", None) or getattr(c, "main", None)
    print(fn() if fn else "dcs.tests.conformance: no entry point")

def _coherence(argv):
    from dcs import coherence
    fn = getattr(coherence, "report", None) or getattr(coherence, "main", None)
    print(fn() if fn else "dcs.coherence: no entry point")

def _balance(argv):
    p = argparse.ArgumentParser(); p.add_argument("--floor", type=int, default=12)
    a = p.parse_args(argv)
    from dcs import balance
    fn = getattr(balance, "render", None) or getattr(balance, "report", None)
    print(fn(floor=a.floor) if fn else "dcs.balance: no entry point")

def _converge(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--floor", type=int, default=12)
    p.add_argument("--max-steps", type=int, default=40)
    p.add_argument("--write", action="store_true")
    a = p.parse_args(argv)
    from dcs import balance
    fn = getattr(balance, "converge", None)
    print(fn(floor=a.floor, max_steps=a.max_steps, write=a.write) if fn else "dcs.balance: no converge()")

EXTRA = {"coordinate": _coordinate, "conformance": _conformance,
         "coherence": _coherence, "balance": _balance, "converge": _converge}

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] in EXTRA:
        return EXTRA[argv[0]](argv[1:])
    return _cli_orig.main()

if __name__ == "__main__":
    sys.exit(main())
'''
    cli.write_text(wrapper)
    ast.parse(wrapper)
    note("[cli.py] wrapper installed (+coordinate, conformance, coherence, balance, converge)")
elif orig.exists():
    note("[cli.py] wrapper already in place")

# ── 9. purge caches + editable install ───────────────────────
subprocess.run("find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null", shell=True)
note("")
note("=" * 60)
r = subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(ROOT)],
                   capture_output=True, text=True)
if r.returncode == 0:
    last = [l for l in r.stdout.splitlines() if "Successfully" in l or "Installing" in l][-3:]
    note("[pip] " + " | ".join(last) if last else "[pip] ok")
else:
    note("[pip] FAILED: " + r.stderr.strip().splitlines()[-1][:200])
note("=" * 60)

# ── 10. verification ─────────────────────────────────────────
def run(cmd, grep=None, tail=None):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    out = r.stdout
    if grep: out = "\n".join(l for l in out.splitlines() if re.search(grep, l))
    if tail: out = "\n".join(out.splitlines()[-tail:])
    return out.strip() or "(no output)"

note("\n### dcs --help (choices line)")
note(run("python -m dcs --help 2>&1 | head -4"))
note("\n### dcs laws")
note(run("python -m dcs laws 2>&1 | grep -E '✗|n_passed|n_failed'"))
note("\n### dcs conform (fails + summary)")
note(run("python -m dcs conform 2>&1 | grep -E 'FAIL|MUST_pass|MUST_fail|SHOULD_fail|verdict'"))
note("\n### dcs coordinate")
note(run("python -m dcs coordinate 2>&1 | tail -4"))
note("\n### dcs balance --floor 12")
note(run("python -m dcs balance --floor 12 2>&1 | tail -4"))

note(f"\nBackups: {backup}")
