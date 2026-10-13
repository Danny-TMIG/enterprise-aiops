#!/usr/bin/env python3
"""Self compile · build · run · observe · observe-the-observation · A–Z.

One pass. Reports what is true. Writes every phase to the ledger so the
next run's observation is on top of the previous run.

    Phase C  compile   py_compile every .py under app/
    Phase B  build     import every module; autoload every capability
    Phase R  run       pytest -q
    Phase O  observe   read the ledger, summarize
    Phase N  nested    observe the observation (meta-record)
    Phase AZ A–Z       per-letter capability census + dispatch probe
"""
from __future__ import annotations

import hashlib
import importlib
import json
import py_compile
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core import capabilities as caps
from app.core.ram_substrate import RAMSubstrate

SUB = RAMSubstrate(capacity=4096, autoload=True)


def phase_c_compile() -> dict[str, Any]:
    ok, fail = [], []
    for p in sorted((ROOT / "app").rglob("*.py")):
        if "__pycache__" in str(p):
            continue
        try:
            py_compile.compile(str(p), doraise=True)
            ok.append(str(p.relative_to(ROOT)))
        except py_compile.PyCompileError as e:
            fail.append({"file": str(p.relative_to(ROOT)), "err": str(e)[:200]})
    return {"compiled": len(ok), "failed": len(fail), "failures": fail[:8]}


def phase_b_build() -> dict[str, Any]:
    # collect every capability code from the table
    from app.core.capabilities import CAPS
    loaded, failed = [], []
    for code, name, cat, eq, st, prov, home in CAPS:
        if st != "real" or not home:
            continue
        mod = home[:-3].replace("/", ".") if home.endswith(".py") else home.replace("/", ".")
        try:
            importlib.import_module(mod)
            loaded.append(mod)
        except Exception as e:
            failed.append({"mod": mod, "err": f"{type(e).__name__}: {e}"[:200]})
    return {"modules_loaded": len(set(loaded)), "modules_failed": len(failed),
            "failures": failed[:8]}


def phase_r_run() -> dict[str, Any]:
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header",
         "-p", "no:cacheprovider", "--tb=line", "tests/"],
        cwd=str(ROOT), capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONPATH": str(ROOT)},
    )
    tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
    m = re.search(r"(\d+) passed", r.stdout + r.stderr)
    f = re.search(r"(\d+) failed", r.stdout + r.stderr)
    return {"rc": r.returncode,
            "passed": int(m.group(1)) if m else 0,
            "failed": int(f.group(1)) if f else 0,
            "tail": tail}


def phase_o_observe() -> dict[str, Any]:
    return {
        "resident": SUB.stats()["resident"],
        "head_seq": SUB.stats()["head_seq"],
        "head_hash": SUB.stats()["head_hash"],
        "subjects": SUB.stats()["subjects"],
        "kinds": sorted({e.kind for e in SUB.tail(500)}),
        "recent": [{"seq": e.seq, "kind": e.kind, "subject": e.subject}
                   for e in SUB.tail(8)],
        "chain": SUB.verify_chain()["ok"],
    }


def phase_n_nested(prev: dict[str, Any]) -> dict[str, Any]:
    """Observe the observation: hash the summary and record a new event."""
    blob = json.dumps(prev, sort_keys=True, default=str)
    h = hashlib.sha256(blob.encode()).hexdigest()[:16]
    return {"observed_hash": h, "observed_size": len(blob),
            "subjects_observed": prev["subjects"]}


def phase_az_census() -> dict[str, Any]:
    """Per-letter census of capability codes + a live dispatch probe."""
    census: dict[str, int] = {}
    for code, *_ in caps.CAPS:
        letter = code[0].upper()
        census[letter] = census.get(letter, 0) + 1
    # dispatch probe: real ones we expect to work
    probe_codes = [c for c, *_ in caps.CAPS if c.startswith("catch_release")]
    probe = []
    for code in probe_codes:
        d = caps.dispatch(code)
        probe.append({"code": code, "ok": d.ok, "status": d.status})
    # also probe the substrate capability itself
    return {"letters": dict(sorted(census.items())),
            "codes": sum(census.values()),
            "probe": probe}


def main() -> int:
    print("═══ selfrun ═══")
    t0 = time.time()

    print("\n── C compile ──")
    c = phase_c_compile()
    SUB.append("selfrun.compile", "app", c)
    print(f"  compiled {c['compiled']}  failed {c['failed']}")
    for f in c["failures"]:
        print(f"    ! {f['file']}: {f['err'][:80]}")

    print("\n── B build ──")
    b = phase_b_build()
    SUB.append("selfrun.build", "app", b)
    print(f"  modules_loaded {b['modules_loaded']}  failed {b['modules_failed']}")
    for f in b["failures"]:
        print(f"    ! {f['mod']}: {f['err'][:80]}")

    print("\n── R run ──")
    r = phase_r_run()
    SUB.append("selfrun.run", "tests", r)
    print(f"  rc={r['rc']}  passed={r['passed']}  failed={r['failed']}")
    for line in r["tail"]:
        print(f"    {line}")

    print("\n── O observe ──")
    o = phase_o_observe()
    SUB.append("selfrun.observe", "ledger", o)
    print(f"  resident={o['resident']}  head={o['head_seq']}  chain={o['chain']}")
    print(f"  kinds={o['kinds']}")

    print("\n── N nested ──")
    n = phase_n_nested(o)
    SUB.append("selfrun.nested", "ledger", n)
    print(f"  observed_hash={n['observed_hash']}  size={n['observed_size']}")

    print("\n── A–Z census ──")
    az = phase_az_census()
    SUB.append("selfrun.census", "capabilities", az)
    letters = az["letters"]
    for letter in sorted(letters):
        print(f"    {letter}: {letters[letter]}")
    print(f"  codes={az['codes']}")
    for p in az["probe"]:
        print(f"    probe {p['code']}: ok={p['ok']} status={p['status']}")

    # final chain verify after all writes
    print("\n── chain verify (after all writes) ──")
    v = SUB.verify_chain()
    print(f"  ok={v['ok']}  checked={v.get('checked')}  head={v.get('head','')[:16]}…")

    print(f"\n  elapsed {time.time() - t0:.2f}s")
    return 0 if v["ok"] and r["rc"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
