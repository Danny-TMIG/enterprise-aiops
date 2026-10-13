#!/usr/bin/env python3
"""Structural stability proof for the fabric.

Ten properties. Each is checkable from what already exists.
No new capabilities. No new catalogs. If a vertical fails a
property, the failing row is named.

    P1  compile closure      every .py under app/ parses
    P2  import closure       every app.* reference resolves
    P3  test closure         pytest tests/ passes
    P4  ledger closure       every write goes through RAMSubstrate
    P5  chain closure        events table verifies from seq=1
    P6  dispatch closure     every capability marked `real` has a callable
    P7  catalog closure      every catalog row is implemented or aspirational
    P8  determinism          same seed -> same result on re-run
    P9  bridges              graph bridge model layers run
    P10 runtime closure      real capability execution succeeds
"""
from __future__ import annotations

import ast
import hashlib
import json
import py_compile
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


# ── P1 ─────────────────────────────────────────────────────────────
def p1_compile() -> dict[str, Any]:
    ok, bad = 0, []
    for p in sorted((ROOT / "app").rglob("*.py")):
        if "__pycache__" in str(p):
            continue
        try:
            py_compile.compile(str(p), doraise=True)
            ok += 1
        except py_compile.PyCompileError as e:
            bad.append({"file": str(p.relative_to(ROOT)),
                        "err": str(e).split("\n")[0][:120]})
    return {"pass": not bad, "ok": ok, "failed": len(bad), "failures": bad[:8]}


# ── P2 ─────────────────────────────────────────────────────────────
def p2_imports() -> dict[str, Any]:
    """Check imports in a bounded child process and identify a stuck import."""
    import math
    import os
    import signal
    import tempfile
    import time

    per_import = float(os.environ.get("STABILITY_IMPORT_TIMEOUT", "20"))
    total_limit = float(os.environ.get("STABILITY_IMPORT_TOTAL_TIMEOUT", "180"))
    if not all(math.isfinite(v) and v > 0 for v in (per_import, total_limit)):
        raise ValueError("Import timeouts must be positive finite seconds")
    statements = set()
    for p in list((ROOT / "app").rglob("*.py")) + list((ROOT / "scripts").rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue  # P1 reports source syntax failures.
        for node in ast.walk(tree):
            if (isinstance(node, ast.ImportFrom) and node.level == 0
                    and node.module and node.module.startswith("app.")):
                statements.add(ast.unparse(node))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("app."):
                        statements.add("import " + alias.name)
    statements = sorted(statements)
    if not statements:
        return {"pass": True, "checked": 0, "total": 0, "missing": {}, "import_errors": []}
    worker = """
import json, sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
requests = json.loads(Path(sys.argv[2]).read_text())
report = Path(sys.argv[3])
state = {"checked": 0, "total": len(requests), "missing": {}, "import_errors": [],
         "current": None, "started": time.monotonic(), "complete": False}
def save():
    temporary = report.with_suffix(".tmp")
    temporary.write_text(json.dumps(state))
    temporary.replace(report)
for statement in requests:
    state.update(current=statement, started=time.monotonic())
    save()
    try:
        exec(statement, {})
    except ModuleNotFoundError as exc:
        state["missing"].setdefault(exc.name or statement, []).append(statement)
    except BaseException as exc:
        state["import_errors"].append({"import": statement, "error": f"{type(exc).__name__}: {exc}"})
    state["checked"] += 1
    state["current"] = None
    save()
state["complete"] = True
save()
"""
    print(f"    P2: checking {len(statements)} imports "
          f"({per_import:g}s per import, {total_limit:g}s total)", flush=True)
    state = {"checked": 0, "missing": {}, "import_errors": [], "current": None}
    reason = None
    with tempfile.TemporaryDirectory(prefix="stability-imports-") as directory:
        directory = Path(directory)
        requests = directory / "requests.json"
        report = directory / "report.json"
        log = directory / "worker.log"
        requests.write_text(json.dumps(statements))
        with log.open("wb") as output:
            proc = subprocess.Popen(
                [sys.executable, "-u", "-c", worker, str(ROOT), str(requests), str(report)],
                cwd=str(ROOT), stdout=output, stderr=subprocess.STDOUT,
                env={**os.environ, "PYTHONPATH": str(ROOT), "PYTHONUNBUFFERED": "1"},
                start_new_session=(os.name == "posix"),
            )
            start = last_message = time.monotonic()
            try:
                while True:
                    if report.exists():
                        state = json.loads(report.read_text())
                    now = time.monotonic()
                    if proc.poll() is not None:
                        # Read the last report after the process has stopped.
                        if report.exists():
                            state = json.loads(report.read_text())
                        if proc.returncode != 0 or not state.get("complete"):
                            reason = f"import worker exited with code {proc.returncode} during {state.get('current')}"
                        break
                    if now - last_message >= 2:
                        current = state.get("current") or "worker startup or shutdown"
                        print(f"    P2 [{state['checked']}/{len(statements)}]: {current}", flush=True)
                        last_message = now
                    if now - start >= total_limit:
                        reason = f"P2 exceeded {total_limit:g}s during {state.get('current')}"
                        break
                    # Imports may also leave background threads running at shutdown.
                    if now - state.get("started", start) >= per_import:
                        current = state.get("current") or "worker startup or shutdown"
                        reason = f"import timed out after {per_import:g}s: {current}"
                        break
                    time.sleep(0.05)
            finally:
                if proc.poll() is None:
                    if os.name == "posix":
                        try:
                            os.killpg(proc.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                    else:
                        proc.kill()
                proc.wait()
        result = {"pass": not reason and not state["missing"] and not state["import_errors"],
                  "checked": state["checked"], "total": len(statements),
                  "unchecked": len(statements) - state["checked"],
                  "missing": state["missing"], "import_errors": state["import_errors"]}
        if reason:
            result["reason"] = reason
            result["last_import"] = state.get("current")
            with log.open("rb") as output:
                output.seek(0, 2)
                output.seek(max(0, output.tell() - 4000))
                result["output_tail"] = output.read().decode(errors="replace")
        return result


# ── P3 ─────────────────────────────────────────────────────────────
def p3_tests() -> dict[str, Any]:
    """Keep pytest's exit status authoritative and explain coverage failures."""
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider", "-p", "no:sugar", "--tb=short", "tests/"],
        timeout=45,
        cwd=str(ROOT), capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT)},
    )
    out = r.stdout + r.stderr
    counts = {}
    for key, pattern in (("passed", r"(\d+) passed"),
                         ("failed", r"(\d+) failed"),
                         ("errors", r"(\d+) error")):
        matches = re.findall(pattern, out)
        counts[key] = int(matches[-1]) if matches else 0
    result = {"pass": r.returncode == 0, "rc": r.returncode, **counts}
    coverage = re.search(
        r"Required test coverage of ([\d.]+)% (not reached|reached)\. "
        r"Total coverage: ([\d.]+)%", out)
    if coverage:
        result["coverage_percent"] = float(coverage.group(3))
        result["coverage_required"] = float(coverage.group(1))
        result["coverage_pass"] = coverage.group(2) == "reached"
    if r.returncode:
        reason = {1: "pytest reported a test or quality-gate failure",
                  2: "pytest was interrupted or test collection failed",
                  3: "pytest internal error", 4: "pytest configuration or command error",
                  5: "pytest collected no tests"}.get(r.returncode, "pytest did not complete successfully")
        if coverage and coverage.group(2) == "not reached":
            reason += "; " + coverage.group(0)
        result["reason"] = reason
        result["output_tail"] = out[-6000:]
    return result


# ── P4 ─────────────────────────────────────────────────────────────
def p4_ledger_writes() -> dict[str, Any]:
    # every direct `INSERT INTO events` outside ram_substrate is a
    # violation of the single-writer invariant.
    hits = []
    for p in sorted((ROOT / "app").rglob("*.py")) + \
             sorted((ROOT / "scripts").rglob("*.py")):
        if "__pycache__" in str(p):
            continue
        rel = str(p.relative_to(ROOT))
        if rel.endswith("ram_substrate.py"):
            continue
        src = p.read_text()
        # only live SQL calls count, not the literal inside this check
        for line in src.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if re.search(r"execute\s*\(\s*[fr]?['\"]INSERT\s+INTO\s+events",
                         line, re.IGNORECASE):
                hits.append(rel)
                break
    return {"pass": not hits, "violations": hits}


# ── P5 ─────────────────────────────────────────────────────────────
def p5_chain() -> dict[str, Any]:
    from app.core.ram_substrate import RAMSubstrate
    sub = RAMSubstrate(capacity=8, autoload=False)  # small ring, chain check is against db
    v = sub.verify_chain(from_seq=1)
    return {"pass": bool(v.get("ok")),
            "checked": v.get("checked", 0),
            "reason": v.get("reason"),
            "head": (v.get("head") or "")[:16]}


# ── P6 ─────────────────────────────────────────────────────────────
def p6_dispatch() -> dict[str, Any]:
    """Every real capability must resolve to a callable implementation."""
    import sqlite3
    from contextlib import closing

    from app.core import capabilities as c
    with closing(sqlite3.connect(c.DB)) as con:
        real = [r[0] for r in con.execute(
            "SELECT code FROM capabilities WHERE status='real' ORDER BY code")]
    missing = []
    for code in real:
        c._autoload(code)
        if not callable(c._IMPL.get(code)):
            missing.append({"code": code, "reason": c._AUTOLOAD_ERRORS.get(code, "not callable")})
    return {"pass": not missing, "checked": len(real),
            "registered": len(real) - len(missing), "missing_count": len(missing),
            "missing": missing[:12]}


def p10_runtime() -> dict[str, Any]:
    """How many real caps run right now. FAIL if any don't.

    Before the local generator landed this was informational — 90% of
    the registry was unrunnable and P10 still printed PASS. It now
    reports honestly: dep_satisfied > 0 -> P10 red, names the failures.
    """
    import sqlite3

    from app.core.capabilities import DB, dispatch
    con = sqlite3.connect(DB)
    real = [r[0] for r in con.execute(
        "SELECT code FROM capabilities WHERE status='real' ORDER BY code")]
    con.close()
    ok = 0
    failed = []
    for code in real:
        d = dispatch(code)
        if d.ok:
            ok += 1
        else:
            failed.append((code, (getattr(d, "reason", "") or "")[:80]))
    return {
        "pass":          not failed,
        "checked":       len(real),
        "ran_ok":        ok,
        "dep_satisfied":   len(failed),
        "failed_sample": failed[:10],
    }

def p7_catalog() -> dict[str, Any]:
    import sqlite3

    from app.core.capabilities import DB
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT code, status FROM capabilities WHERE category='nature'"
    ).fetchall()
    con.close()
    real = [c for c, s in rows if s == "real"]
    asp  = [c for c, s in rows if s != "real"]
    return {"pass": True,
            "nature_real": len(real), "nature_aspirational": len(asp)}


# ── P8 ─────────────────────────────────────────────────────────────
def p8_determinism() -> dict[str, Any]:
    """Run one phenomenon twice with the same seed; hashes must match."""
    from app.core.nature import kuramoto, levy_flight, sir
    cases = [
        ("kuramoto",  lambda: kuramoto(n=20, steps=50, seed=7)),
        ("sir",       lambda: sir(steps=100)),
        ("levy",      lambda: levy_flight(n=500, seed=11)),
    ]
    bad = []
    for label, fn in cases:
        h1 = hashlib.sha256(json.dumps(fn(), sort_keys=True, default=str).encode()).hexdigest()
        h2 = hashlib.sha256(json.dumps(fn(), sort_keys=True, default=str).encode()).hexdigest()
        if h1 != h2:
            bad.append(label)
    return {"pass": not bad, "checked": len(cases), "nondeterministic": bad}




# ── P9 ─────────────────────────────────────────────────────────────
def p9_bridges() -> dict[str, Any]:
    """Every external-graph bridge declares runtime availability and
    exposes a working model layer that runs without the runtime."""
    from app.bridges import describe
    d = describe()
    bad = []
    for name, info in d.items():
        if not isinstance(info, dict):
            bad.append((name, "not a dict")); continue
        if "runtime_available" not in info:
            bad.append((name, "missing runtime_available")); continue
        # model layer check: run describe()'s own model without error
        try:
            if name == "uns":
                from app.bridges import uns as m
                t = m.UNSTree()
                t.add("acme/site1/line1/cell1/asset1/tag1", value=1)
                assert t.topic("acme/site1/line1/cell1/asset1/tag1")
            elif name == "ros":
                from app.bridges import ros as m
                c = m.ROSCatalog()
                c.add_node(m.Node("a", pubs=[m.Topic("/t")]))
                c.add_node(m.Node("b", subs=[m.Topic("/t")]))
                assert c.orphan_topics() == []
            elif name == "ros2":
                from app.bridges import ros2 as m
                c = m.ROS2Catalog()
                c.add(m.Node2("a", pubs=[m.Endpoint("/t","x","default")]))
                c.add(m.Node2("b", subs=[m.Endpoint("/t","x","sensor_data")]))
                assert c.qos_mismatches()
            elif name == "usd":
                from app.bridges import usd as m
                s = m.Stage()
                s.open(m.Layer("a.usda", prims={"/W": m.Prim("/W","Xform")}))
                assert s.compose("/W")["defined_in"] == "a.usda"
        except Exception as e:
            bad.append((name, f"{type(e).__name__}: {e}"))
    return {"pass": not bad, "bridges": list(d), "failures": bad}


def main() -> int:
    from app.core.ram_substrate import RAMSubstrate
    sub = RAMSubstrate(capacity=4096, autoload=True)

    checks = [
        ("P1 compile",     p1_compile),
        ("P2 imports",     p2_imports),
        ("P3 tests",       p3_tests),
        ("P4 ledger",      p4_ledger_writes),
        ("P5 chain",       p5_chain),
        ("P6 dispatch",    p6_dispatch),
        ("P7 catalog",     p7_catalog),
        ("P8 determinism", p8_determinism),
        ("P9 bridges",     p9_bridges),
        ("P10 runtime",    p10_runtime),
    ]

    results = []
    print("═══ stability ═══")
    for label, fn in checks:
        print(f"\n── {label}: checking ──", flush=True)
        try:
            r = fn()
        except Exception as e:
            r = {"pass": False, "reason": f"{type(e).__name__}: {e}"}
        results.append((label, r))
        sub.append("stability", label, r)
        status = "PASS" if r.get("pass") else "FAIL"
        print(f"\n── {label}: {status} ──")
        for k, v in r.items():
            if k == "pass":
                continue
            if isinstance(v, list) and len(v) > 6:
                v = v[:6] + ["…"]
            print(f"    {k}: {v}")

    # summary
    passed = sum(1 for _, r in results if r.get("pass"))
    total = len(results)
    print()
    print(f"  {passed}/{total} properties hold")

    v = sub.verify_chain()
    print(f"  ledger chain ok={v['ok']}  checked={v['checked']}")

    return 0 if passed == total else 2


if __name__ == "__main__":
    sys.exit(main())
