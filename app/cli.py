"""Unified entry point: python3 -m app <cmd> [args]"""
from __future__ import annotations

import argparse
import json
import sys


def _supply(argv):
    from pathlib import Path

    from app.supply.attest import build_attestation, verify_attestation
    from app.supply.sbom import build_sbom, sbom_digest
    from app.supply.sign import generate_key, key_id, sign
    root = Path.cwd()
    sbom = build_sbom("enterprise_aiops", "0.1.0", root)
    d = sbom_digest(sbom)
    key = generate_key()
    sig = sign(json.dumps(sbom, sort_keys=True).encode(), key)
    att = build_attestation(sbom, key)
    ok = verify_attestation(att, key)
    out = root / "dist"
    out.mkdir(exist_ok=True)
    (out / "sbom.cdx.json").write_text(json.dumps(sbom, indent=2))
    (out / "sbom.sig").write_text(sig)
    (out / "sbom.att.json").write_text(json.dumps(att, indent=2))
    (out / "key.id").write_text(key_id(key))
    print(f"  components: {len(sbom['components'])}")
    print(f"  sbom digest: {d[:16]}")
    print(f"  key id:      {key_id(key)}")
    print(f"  signature:   {sig[:16]}...")
    print(f"  attestation: verify={ok}")
    print(f"  wrote: {out}/sbom.cdx.json")
    print(f"         {out}/sbom.sig")
    print(f"         {out}/sbom.att.json")

def _policy(argv):
    from app.policy.parser import evaluate, parse_policy
    p = argparse.ArgumentParser(prog="app policy")
    p.add_argument("file", nargs="?")
    p.add_argument("--ctx", default="{}")
    p.add_argument("--check", action="store_true")
    a = p.parse_args(argv)
    src = open(a.file).read() if a.file else 'rule "deny_high" when severity >= 3 then deny "too high"\nrule "allow_low" when severity < 3 then allow "ok"'
    rules = parse_policy(src)
    print(f"  parsed {len(rules)} rules")
    if a.check:
        for r in rules:
            print(f"    {r.name}: when {r.condition} -> {r.action}")
        return
    ctx = json.loads(a.ctx)
    res = evaluate(rules, ctx)
    print(f"  ctx={ctx}  ->  {res}")

def _braid(argv):
    from app.braid.parser import compile_workflow, parse_workflow
    p = argparse.ArgumentParser(prog="app braid")
    p.add_argument("file", nargs="?")
    a = p.parse_args(argv)
    src = open(a.file).read() if a.file else (
        'workflow demo {\n'
        '  source a = fetch("http://x")\n'
        '  source b = fetch("http://y")\n'
        '  braid c = a + b\n'
        '  transform d = c |> verify\n'
        '  emit d\n'
        '}\n')
    wf = parse_workflow(src)
    plan = compile_workflow(wf)
    print(json.dumps(plan, indent=2))

def _cd(argv):
    from app.cd_nand.compute import nand_cd, verify_all_levels
    r = verify_all_levels(6)
    print(f"  CD NAND verify all levels 0..6: {r}")
    for a in (False, True):
        for b in (False, True):
            print(f"    nand_cd({a},{b},level=3) = {nand_cd(a, b, 3)}")

def _atlas(argv):
    from app.atlas.algorithms import ALGORITHMS
    from app.atlas.algorithms import validate as av
    from app.atlas.moats import all_moats
    from app.atlas.moats import validate as mv
    print(f"  algorithms: {len(ALGORITHMS)}  {av()}")
    print(f"  moats:      {len(all_moats())}  {mv()}")

def main(argv=None):
    if argv is None: argv = sys.argv[1:]
    if not argv:
        print("usage: python3 -m app {supply|policy|braid|cd|atlas}")
        return 1
    cmd, rest = argv[0], argv[1:]
    return {"supply": _supply, "policy": _policy, "braid": _braid,
            "cd": _cd, "atlas": _atlas}.get(cmd, lambda _: 1)(rest) or 0

if __name__ == "__main__":
    sys.exit(main())
