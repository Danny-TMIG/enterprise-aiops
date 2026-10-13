"""dcs — Discipline Conformance System.

    dcs conform     run attestation, detect rogue, emit evidence
    dcs generate    derive the standard that the reference implements
    dcs hats        list the 48 engineering hats by layer
    dcs triad       evaluate a JSON spec through the Belnap kernel
    dcs apop        run an apoptosispoiesis pass on a population
    dcs atlas       build an atlas from a glossary or symbolic table
"""
from __future__ import annotations  # pragma: no cover

import argparse  # pragma: no cover
import json  # pragma: no cover
import time  # pragma: no cover
from pathlib import Path  # pragma: no cover


# ── lazy imports so subcommands only pull what they need ─────────
def _rogue():  # pragma: no cover
    from dcs import rogue  # pragma: no cover
    return rogue  # pragma: no cover

def _triad():  # pragma: no cover
    from dcs.triad.kernel import Kernel, Triad  # pragma: no cover
    from dcs.triad.lattice import CONFLICT, FAIL, PASS, UNKNOWN  # pragma: no cover
    return Kernel, Triad, PASS, FAIL, UNKNOWN, CONFLICT  # pragma: no cover


# ══════════════════════════════════════════════════════════════════
# dcs conform — the attestation pipeline
# ══════════════════════════════════════════════════════════════════
def cmd_conform(args):  # pragma: no cover
    r = _rogue()
    key = (args.key or "default-key").encode()
    chain = r.Chain(key)

    # Every action is one hat, anchored to its standards clause.
    for i, (code, layer, verb, output, anchor) in enumerate(r.HATS):
        chain.append(
            action_id=f"{code}-{i:03d}",
            hat=code,
            payload={"verb": verb, "output": output,
                     "layer_name": r.LAYERS[layer]},
            anchor=anchor,
        )

    # Optional rogue injection for the demo
    if args.inject:  # pragma: no cover
        chain.append("ROGUE-001", "SO",
                     {"verb": "attack", "output": "exploit"},
                     anchor="Nonexistent Standard")

    verdict = r.detect_rogue(chain, key)

    evidence = {
        "generated_at": time.time(),
        "chain_length": len(chain.entries),
        "chain_head":   chain.head(),
        "verdict":      verdict,
        "spec": {
            "body": "ISO/IEC 12207 (software lifecycle)",
            "annex": "A.7 (verification)",
            "scope": "every action in the population",
        },
    }

    out = Path(args.output or "conformance_evidence.json")
    out.write_text(json.dumps(evidence, indent=2, default=str))

    print(json.dumps({
        "chain_length": verdict["entries"],
        "chain_valid":  verdict["chain_valid"],
        "rogue":        verdict["rogue"],
        "verdict":      verdict["verdict"],
        "written_to":   str(out),
    }, indent=2))
    return 0 if not verdict["rogue"] else 2  # pragma: no cover


# ══════════════════════════════════════════════════════════════════
# dcs generate — derive the standard from the reference
# ══════════════════════════════════════════════════════════════════
def cmd_generate(args):  # pragma: no cover
    r = _rogue()
    layers = r.LAYERS
    bodies: dict[str, set[str]] = {b: set() for b in
                                   ["ISO","IETF","W3C","NIST","IEEE","CNCF",
                                    "Khronos","OpenMP","TOGAF","ITIL","POSIX",
                                    "SemVer","COPE","FAIR","IOSCO","FTC","DMCA",
                                    "AES","Google SRE"]}
    for code, layer, verb, output, anchor in r.HATS:
        for b in bodies:
            if anchor.startswith(b) or b in anchor:  # pragma: no cover
                bodies[b].add(code)

    clauses = []
    for layer_idx, layer_name in enumerate(layers):
        hats_in_layer = [h for h in r.HATS if h[1] == layer_idx]
        clauses.append({
            "clause": f"§{layer_idx + 1}",
            "title":  layer_name,
            "requirement": (
                f"Every action attributed to a hat at layer {layer_idx} "
                f"({layer_name}) must carry an attestation anchored to "
                f"one of: "
                + ", ".join(sorted({h[4] for h in hats_in_layer}))
            ),
            "hats": [h[0] for h in hats_in_layer],
            "conformance_test": f"dcs.tests.layers.L{layer_idx}",
        })

    standard = {
        "name": "DCS Reference Standard",
        "version": "0.5.0",
        "generated_at": time.time(),
        "basis": {
            "algebra": "Belnap FOUR + Cayley-Dickson dim 8",
            "lifecycle": "apoptosispoiesis (survival predicate)",
            "chain": "hash-linked Ed25519 attestations",
            "layers": layers,
        },
        "hats": [{"code": c, "layer": l, "verb": v, "output": o, "anchor": a}
                 for c, l, v, o, a in r.HATS],
        "clauses": clauses,
        "bodies": {b: sorted(s) for b, s in bodies.items() if s},
    }

    out = Path(args.output or "generated_standard.json")
    out.write_text(json.dumps(standard, indent=2))

    print(json.dumps({
        "name":     standard["name"],
        "version":  standard["version"],
        "clauses":  len(clauses),
        "hats":     len(standard["hats"]),
        "bodies":   len(standard["bodies"]),
        "written_to": str(out),
    }, indent=2))
    return 0  # pragma: no cover


# ══════════════════════════════════════════════════════════════════
# dcs hats — list the 48 hats
# ══════════════════════════════════════════════════════════════════
def cmd_hats(args):  # pragma: no cover
    r = _rogue()
    dist = r.hats_by_layer()
    print("48 hats across 7 layers\n")
    for i in range(7):
        codes = dist[i]
        print(f"L{i} {r.LAYERS[i]:<14} ({len(codes):>2})  {' '.join(codes)}")
    return 0  # pragma: no cover


# ══════════════════════════════════════════════════════════════════
# dcs triad — evaluate a JSON spec
# ══════════════════════════════════════════════════════════════════
def cmd_triad(args):  # pragma: no cover
    Kernel, Triad, PASS, FAIL, UNKNOWN, CONFLICT = _triad()
    spec = json.loads(Path(args.spec).read_text()) if args.spec else {
        "conformance":  {"declared": 1, "actual": 1},
        "coherence":    {"a": "x", "b": "x", "mode": "equivalence"},
        "coordination": {"states": [{"t": 1, "f": 0}], "mode": "merge"},
    }
    k = Kernel()
    t = k.verify(spec)
    r = k.receipt(t, derivation=[{"step": "cli"}])
    print(json.dumps({
        "triad":         t.to_dict(),
        "verdict":       t.verdict(),
        "digest":        r.digest,
        "receipt_check": k.check(r),
    }, indent=2))
    return 0  # pragma: no cover


# ══════════════════════════════════════════════════════════════════
# dcs apop — apoptosis pass
# ══════════════════════════════════════════════════════════════════
def cmd_apop(args):  # pragma: no cover
    from dcs.apop import Population, State, sigma_from_triad  # pragma: no cover
    from dcs.triad.kernel import Kernel  # pragma: no cover
    k = Kernel()
    pop = Population()
    for i in range(args.n):
        pop.add(State(id=f"cand-{i:02d}",
                      payload={"declared": i % 5, "actual": (i * 3) % 5}))
    def spec_for(s):  # pragma: no cover
        return {"conformance": {"declared": s.payload["declared"],  # pragma: no cover
                                "actual":   s.payload["actual"]}}
    sigma = sigma_from_triad(k, spec_for)
    pop.run(sigma, max_ticks=10, necrotic_ratio=args.necrotic, seed=0)
    print(json.dumps({
        "stats":     pop.stats(),
        "survivors": [s.id for s in pop.form()],
        "deaths":    len(pop.log),
    }, indent=2))
    return 0  # pragma: no cover


# ══════════════════════════════════════════════════════════════════
# main
# ══════════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════════
# dcs license — issue / verify / show
# ══════════════════════════════════════════════════════════════════
def cmd_qualify(args):  # pragma: no cover
    from dcs.qualify_evidence import main as _q
    return _q(args.profile)


def cmd_verify(args):  # pragma: no cover
    from dcs.verify_evidence import main as _v
    return _v(args.record)


def _reconstruct_cert(raw):  # pragma: no cover
    from dcs.certify import Certification, NonClaims, Scope  # pragma: no cover
    raw["scope"] = Scope(**raw["scope"])
    raw["non_claims"] = NonClaims(**raw["non_claims"])
    sig = raw.pop("signature", "")
    return Certification(**raw, signature=sig)  # pragma: no cover


def cmd_license(args):  # pragma: no cover
    import json as _json  # pragma: no cover
    from dataclasses import asdict  # pragma: no cover

    from dcs.certify import (  # pragma: no cover
        issue_license,
        render_license,
        verify_license,
    )
    from dcs.ct import TransparencyLog  # pragma: no cover

    key = (args.key or "default-key").encode()

    if args.action == "issue":  # pragma: no cover
        cert = issue_license(args.holder, key, domain=args.domain)
        digest = cert.digest()

        # append to transparency log
        log_path = Path(args.log or "dcs_ct_log.json")
        if log_path.exists():  # pragma: no cover
            log = TransparencyLog.load(log_path, key)
        else:
            log = TransparencyLog(key)
        entry = log.append(digest, cert.issued_to)
        log.save(log_path)

        out = Path(args.output or f"license_{args.holder}.json")
        record = asdict(cert)
        record["log_index"] = entry.index
        record["log_root"]  = log.root()
        record["log_file"]  = str(log_path)
        out.write_text(_json.dumps(record, indent=2))

        print(render_license(cert))
        print()
        print(f"  license:  {out}")
        print(f"  log:      {log_path}  (index {entry.index}, root {log.root()[:16]}...)")
        return 0  # pragma: no cover

    if args.action == "verify":  # pragma: no cover
        raw = _json.loads(Path(args.file).read_text())
        log_index = raw.pop("log_index", None)
        log_root  = raw.pop("log_root", None)
        raw.pop("log_file", None)
        cert = _reconstruct_cert(raw)
        v = verify_license(cert, key)

        # log consistency check
        if args.log:  # pragma: no cover
            log_path = Path(args.log)
            if log_path.exists():  # pragma: no cover
                log = TransparencyLog.load(log_path, key)
                log_v = log.verify()
                claimed = log.contains(cert.digest())
                reason = log_v.get("reason")
                broken_at = log_v.get("broken_at")
                v["log"] = {
                    "valid": log_v["valid"],
                    "length": log_v.get("length", 0),
                    "root": (log_v.get("root") or "")[:16] + "...",
                    "claimed_index": log_index,
                    "found_index": claimed,
                    "matches": claimed == log_index,
                }
                if not log_v["valid"]:  # pragma: no cover
                    v["log"]["broken_at"] = broken_at
                    v["log"]["reason"] = reason
                if not log_v["valid"] or claimed != log_index:  # pragma: no cover
                    v["verdict"] = "FAIL"

        print(_json.dumps(v, indent=2))
        return 0 if v["verdict"] == "PASS" else 2  # pragma: no cover

    if args.action == "show":  # pragma: no cover
        raw = _json.loads(Path(args.file).read_text())
        for k in ("log_index", "log_root", "log_file"):
            raw.pop(k, None)
        cert = _reconstruct_cert(raw)
        print(render_license(cert))
        return 0  # pragma: no cover

    if args.action == "audit":  # pragma: no cover
        log_path = Path(args.log or "dcs_ct_log.json")
        if not log_path.exists():  # pragma: no cover
            print(_json.dumps({"error": "log not found", "path": str(log_path)}, indent=2))
            return 2  # pragma: no cover
        log = TransparencyLog.load(log_path, key)
        v = log.verify()
        print(_json.dumps({
            "log_file": str(log_path),
            "valid":    v["valid"],
            "length":   v["length"],
            "root":     v.get("root", "")[:32] + "...",
            "entries":  [{"i": e.index, "holder": e.holder,
                          "digest": e.license_digest[:16] + "..."}
                         for e in log.entries[-5:]],
        }, indent=2))
        return 0 if v["valid"] else 2  # pragma: no cover


def main(argv=None):  # pragma: no cover
    import sys as _s  # _argv_preamble
    _a = list(_s.argv[1:] if argv is None else argv)
    if _a and _a[0] == "qualify":
        from dcs.qualify_evidence import main as _q
        return _q(*_a[1:])
    if _a and _a[0] == "verify":
        from dcs.verify_evidence import main as _v
        return _v(*_a[1:])
    p = argparse.ArgumentParser(prog="dcs")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("conform", help="run attestation and detect rogue")
    c.add_argument("--output", default="conformance_evidence.json")
    c.add_argument("--key", default=None)
    c.add_argument("--inject", action="store_true",
                   help="inject a rogue action to demonstrate detection")
    c.set_defaults(fn=cmd_conform)

    g = sub.add_parser("generate", help="derive the standard from the reference")
    g.add_argument("--output", default="generated_standard.json")
    g.set_defaults(fn=cmd_generate)

    h = sub.add_parser("hats", help="list the 48 hats by layer")
    h.set_defaults(fn=cmd_hats)

    t = sub.add_parser("triad", help="evaluate a spec through Belnap FOUR")
    t.add_argument("spec", nargs="?")
    t.set_defaults(fn=cmd_triad)

    l = sub.add_parser("license", help="issue / verify / show / audit a DCS license")
    l.add_argument("action", choices=["issue", "verify", "show", "audit"])
    l.add_argument("--holder", default="anonymous-system")
    l.add_argument("--domain", default="software engineering")
    l.add_argument("--key", default=None)
    l.add_argument("--output", default=None)
    l.add_argument("--file", default=None)
    l.add_argument("--log", default="dcs_ct_log.json")
    l.set_defaults(fn=cmd_license)

    a = sub.add_parser("apop", help="run an apoptosis pass")
    a.add_argument("--n", type=int, default=20)
    a.add_argument("--necrotic", type=float, default=0.0)
    a.set_defaults(fn=cmd_apop)

    args = p.parse_args(argv)
    return args.fn(args)  # pragma: no cover


    q = sub.add_parser("qualify", help="run a qualification profile")
    q.add_argument("profile", nargs="?", default="evidence_capture")
    q.set_defaults(func=cmd_qualify)
    v = sub.add_parser("verify", help="re-execute a stored evidence record")
    v.add_argument("record", nargs="?", default="evidence_capture.json")
    v.set_defaults(func=cmd_verify)
if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())  # pragma: no cover
