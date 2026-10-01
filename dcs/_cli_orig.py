"""dcs — command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dcs import (
    __version__,
    breadth,
    coalesce,
    conform,
    equivalence,
    generate,
    transparency,
    verify,
)
from dcs import standard as std_mod

ROOT = Path.cwd()
STD = ROOT / "dcs/standards/aiops.json"
EVIDENCE = ROOT / "dcs/evidence"
LOG = ROOT / "dcs/transparency.log"


def _load_std():
    if not STD.exists():
        print(f"standard missing: {STD}", file=sys.stderr)
        sys.exit(2)
    return std_mod.load(STD)


def cmd_generate(args):
    meta = {
        "id": "dcs.aiops",
        "version": "1.0.0",
        "title": "Enterprise AIOps Reference Standard",
        "published": "2026-09-30",
        "authority": "local",
    }
    import pkgutil

    import dcs.hats as _hats

    hat_modules = [
        f"dcs.hats.{m.name}"
        for m in pkgutil.iter_modules(_hats.__path__)
        if not m.name.startswith("_")
    ]
    import dcs.crosscut as _xc

    xc_modules = [
        f"dcs.crosscut.{m.name}"
        for m in pkgutil.iter_modules(_xc.__path__)
        if not m.name.startswith("_")
    ]
    import dcs.nature as _nat

    nat_modules = [
        f"dcs.nature.{m.name}"
        for m in pkgutil.iter_modules(_nat.__path__)
        if not m.name.startswith("_")
    ]
    import dcs.equilibrium as _eq

    eq_modules = [
        f"dcs.equilibrium.{m.name}"
        for m in pkgutil.iter_modules(_eq.__path__)
        if not m.name.startswith("_")
    ]
    out = generate.emit(
        meta,
        [
            "dcs.tests.train",
            "dcs.tests.mesh",
            "dcs.tests.puzzles",
            "dcs.tests.equivalence",
            "dcs.tests.conformance",
            *hat_modules,
            *xc_modules,
            *nat_modules,
            *eq_modules,
        ],
        STD,
    )
    md = generate.render_markdown(json.loads(out.read_text()))
    (out.parent / "aiops.md").write_text(md)
    print(f"wrote {out}")
    print(f"wrote {out.parent / 'aiops.md'}")


def cmd_conform(args):
    std = _load_std()
    key = Path(args.key) if args.key else None
    bundle = conform.run(std, ROOT, sign_key=key)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    import time

    path = EVIDENCE / f"run-{int(time.time())}.json"
    bundle.write(path)
    transparency.append(LOG, bundle.digest, bundle.verdict())
    print(
        json.dumps(
            {
                "bundle": str(path),
                "digest": bundle.digest,
                "verdict": bundle.verdict(),
                "summary": bundle.summary(),
                "signed": bundle.signature is not None,
            },
            indent=2,
        )
    )


def cmd_verify(args):
    report = verify.verify(Path(args.bundle), _load_std_path(), ROOT, re_run=not args.no_replay)
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["integrity"] and report["verdict"] == "CONFORMANT" else 1)


def _load_std_path():
    return STD


def cmd_equivalence_report(args):
    """Exercise every registered equivalence pair on live artifacts."""
    import json

    from app.train import mesh as _mesh
    from app.train.core import TrainConfig, Trainer
    from dcs import standard as _std

    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    r0, r1, r2 = tr.step(0), tr.step(1), tr.step(2)

    artifacts = {
        "Run": (r0, r0),  # reflexive
        "RunSequence": ([r0, r1], [r0, r1]),
        "MeshOfMeshes": (
            _mesh.MeshOfMeshes([r0, r1]),
            _mesh.MeshOfMeshes([r1, r0]),
        ),  # semantic unordered
        "Weave": (_mesh.weave([r0, r1]), _mesh.weave([r0, r1])),
        "CrissCross": (_mesh.criss_cross(r0, r1), _mesh.criss_cross(r0, r1)),
        "Pollinate": (_mesh.pollinate(r0, r1), _mesh.pollinate(r0, r1)),
    }
    if STD.exists():
        std = _std.load(STD)
        artifacts["Standard"] = (std, std)
        artifacts["Requirement"] = (std.requirements[0], std.requirements[0])

    report = {}
    for kind, (a, b) in artifacts.items():
        try:
            report[kind] = {
                "exact": equivalence.exact(kind, a, b),
                "semantic": equivalence.semantic(kind, a, b),
            }
        except KeyError as e:
            report[kind] = {"error": str(e)}
    print(json.dumps(report, indent=2, default=str))


def cmd_coalesce_report(args):
    """Exercise every registered coalescence op on live artifacts."""
    import json

    from app.train import mesh as _mesh
    from app.train.core import TrainConfig, Trainer
    from dcs import standard as _std

    tr = Trainer(TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0))
    r0, r1 = tr.step(0), tr.step(1)

    pairs = [
        ("Run", r0, r0),
        ("RunSequence", [r0], [r1]),
        ("MeshOfMeshes", _mesh.MeshOfMeshes([r0]), _mesh.MeshOfMeshes([r1])),
        ("CrissCross", _mesh.criss_cross(r0, r1), _mesh.criss_cross(r1, r0)),
        ("Pollinate", _mesh.pollinate(r0, r1), _mesh.pollinate(r0, r1)),
    ]
    if STD.exists():
        std = _std.load(STD)
        pairs.append(("Requirement", std.requirements[0], std.requirements[0]))
        pairs.append(("Standard", std, std))

    report = {}
    for kind, a, b in pairs:
        try:
            m1 = coalesce.merge(kind, a, b)
            m2 = coalesce.merge(kind, b, a)
            try:
                comm = equivalence.semantic(kind, m1.value, m2.value)
            except Exception:
                comm = None
            report[kind] = {
                "ok": True,
                "commutative": comm,
                "sources": list(m1.sources),
            }
        except Exception as e:
            report[kind] = {"ok": False, "error": f"{type(e).__name__}: {e}"}
    print(json.dumps(report, indent=2, default=str))


def cmd_equiv(args):
    import json
    from pathlib import Path

    a = json.loads(Path(args.a).read_text()) if Path(args.a).exists() else args.a
    b = json.loads(Path(args.b).read_text()) if Path(args.b).exists() else args.b
    print(
        json.dumps(
            {
                "kind": args.kind,
                "exact": equivalence.exact(args.kind, a, b),
                "semantic": equivalence.semantic(args.kind, a, b),
            },
            indent=2,
        )
    )


def cmd_merge(args):
    import json
    from pathlib import Path

    a = json.loads(Path(args.a).read_text()) if Path(args.a).exists() else args.a
    b = json.loads(Path(args.b).read_text()) if Path(args.b).exists() else args.b
    m = coalesce.merge(args.kind, a, b)
    payload = {
        "kind": args.kind,
        "sources": list(m.sources),
        "value": m.value if isinstance(m.value, (dict, list)) else repr(m.value),
    }
    if args.out:
        Path(args.out).write_text(json.dumps(payload, indent=2, default=str))
        print(f"wrote {args.out}")
    else:
        print(json.dumps(payload, indent=2, default=str))


def cmd_laws(args):
    import json

    from dcs import laws

    report = laws.run_all()
    print(
        json.dumps(
            {k: v for k, v in report.items() if k in ("n_passed", "n_failed", "n_laws")}, indent=2
        )
    )
    for name in report["passed"]:
        print(f"  ✓ {name}")
    for name, err in report["failed"]:
        print(f"  ✗ {name}: {err}")
    return 0 if report["n_failed"] == 0 else 1


def cmd_breadth(args):
    print(breadth.render_matrix(STD))


def cmd_equilibrium(args):
    from dcs import equilibrium

    print(equilibrium.render(STD))


def cmd_conformance(args):
    from dcs.conformance import assess, render

    rep = assess(STD, ROOT)
    print(render(rep))
    return 0 if rep.verdict == "CONFORMANT" else 1


def cmd_coherence(args):
    from dcs.coherence import assess, render

    rep = assess(ROOT, std_path=STD)
    print(render(rep))
    return 0 if rep.coherent else 1


def cmd_coordinate(args):
    import json as _j

    from dcs.team.coord import (
        Epoch,
        quorum,
        reconcile,
        reconcile_associative,
        reconcile_commutative,
        reconcile_idempotent,
    )

    report = {}
    try:
        win, n = quorum(["a", "a", "b"])
        report["quorum"] = {"winner": win, "count": n}
    except Exception as e:
        report["quorum"] = {"error": str(e)}
    _exc = Epoch()
    [_exc.bump() for _ in range(4)]
    report["epoch"] = {"current": _exc.current, "monotonic": _exc.is_monotonic()}
    a = {"x": 1, "y": 2}
    b = {"y": 3, "z": 4}
    report["reconcile"] = {
        "merged": reconcile([a, b]),
        "commutative": reconcile_commutative(a, b),
        "associative": reconcile_associative(a, {"x": 5}, b),
        "idempotent": reconcile_idempotent(a),
    }
    print(_j.dumps(report, indent=2))
    return 0


def cmd_balance(args):
    from dcs import balance

    print(balance.render(floor=getattr(args, "floor", 12)))


def cmd_converge(args):
    from dcs import balance

    print(
        balance.converge(
            floor=getattr(args, "floor", 12),
            max_steps=getattr(args, "max_steps", 40),
            write=getattr(args, "write", False),
        )
    )


def cmd_hats(args):
    from dcs.hats import HATS

    std = _load_std()
    used = {}
    for r in std.requirements:
        for h in r.hats:
            used.setdefault(h, 0)
            used[h] += 1
    for code, name in sorted(HATS.items()):
        n = used.get(code, 0)
        bar = "●" * min(n, 20)
        print(f"  {code:<5} {name:<18} {n:>3}  {bar}")


def cmd_log(args):
    r = transparency.verify_chain(LOG)
    print(json.dumps(r, indent=2))
    if LOG.exists():
        for line in LOG.read_text().splitlines()[-10:]:
            _exc = json.loads(line)
            print(f"  {e['ts']:.0f}  {e['verdict']:<14}  {e['bundle']}")


def cmd_version(args):
    print(f"dcs {__version__}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="dcs", description="Standards & Conformance toolchain")
    p.add_argument("--version", action="version", version=f"dcs {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("generate", help="emit a standard from annotated invariants")
    c = sub.add_parser("conform", help="run the standard; emit evidence")
    c.add_argument("--key", help="hex ed25519 private key (optional)")
    v = sub.add_parser("verify", help="verify an evidence bundle")
    v.add_argument("bundle")
    v.add_argument("--no-replay", action="store_true")
    sub.add_parser("hats", help="requirement counts per engineering hat")
    sub.add_parser("log", help="transparency log status")
    sub.add_parser("laws", help="run the 24-law catalog")
    sub.add_parser("breadth", help="report hat + section coverage")
    sub.add_parser("equilibrium", help="per-hat balance report")

    sub.add_parser("equivalence-report", help="audit equivalence relations project-wide")
    sub.add_parser("coalesce-report", help="audit coalescence operations project-wide")
    _exc = sub.add_parser("equiv", help="compare two artifacts")
    _exc.add_argument("kind")
    _exc.add_argument("a")
    _exc.add_argument("b")
    m = sub.add_parser("merge", help="coalesce two artifacts")
    m.add_argument("kind")
    m.add_argument("a")
    m.add_argument("b")
    m.add_argument("-o", "--out", help="write merged artifact to file")

    args = p.parse_args(argv)
    return {
        "generate": cmd_generate,
        "conform": cmd_conform,
        "verify": cmd_verify,
        "hats": cmd_hats,
        "log": cmd_log,
        "equivalence-report": cmd_equivalence_report,
        "coalesce-report": cmd_coalesce_report,
        "equiv": cmd_equiv,
        "merge": cmd_merge,
        "laws": cmd_laws,
        "breadth": cmd_breadth,
        "equilibrium": cmd_equilibrium,
        "coordinate": cmd_coordinate,
        "conformance": cmd_conformance,
        "coherence": cmd_coherence,
        "balance": cmd_balance,
        "converge": cmd_converge,
    }[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
