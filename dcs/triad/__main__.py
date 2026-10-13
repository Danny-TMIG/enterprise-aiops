"""python -m dcs.triad — CLI."""

import argparse  # pragma: no cover
import json  # pragma: no cover

from dcs.triad.kernel import Kernel  # pragma: no cover
from dcs.triad.report import lattice_diagram, law_report  # pragma: no cover

DEMO_SPEC = {
    "conformance": {"declared": {"a": 1, "b": 2}, "actual": {"a": 1, "b": 2}},
    "coherence": {"a": "hello", "b": "hello", "mode": "equivalence"},
    "coordination": {
        "states": [{"t": 1, "f": 0}, {"t": 1, "f": 0}, {"t": 0, "f": 1}],
        "mode": "quorum",
    },
}


def main(argv=None):  # pragma: no cover
    p = argparse.ArgumentParser(prog="python -m dcs.triad")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lattice", help="print the verification lattice")
    sub.add_parser("laws", help="check the algebraic laws")
    sub.add_parser("self-verify", help="kernel verifies its own outputs")
    sub.add_parser("demo", help="run the built-in demo spec")
    v = sub.add_parser("verify", help="verify a spec from JSON")
    v.add_argument("spec", help="path to JSON spec file")

    args = p.parse_args(argv)
    k = Kernel()

    if args.cmd == "lattice":  # pragma: no cover
        print(lattice_diagram())
    elif args.cmd == "laws":
        print(law_report())
    elif args.cmd == "self-verify":
        t = k.self_verify()
        r = k.receipt(t)
        print(
            json.dumps(
                {
                    "triad": t.to_dict(),
                    "verdict": t.verdict(),
                    "digest": r.digest,
                    "receipt_check": k.check(r),
                },
                indent=2,
            )
        )
    elif args.cmd == "demo":
        t = k.verify(DEMO_SPEC)
        r = k.receipt(
            t, derivation=[{"step": "conformance"}, {"step": "coherence"}, {"step": "coordination"}]
        )
        print(
            json.dumps(
                {
                    "triad": t.to_dict(),
                    "verdict": t.verdict(),
                    "digest": r.digest,
                    "signature": r.signature[:16] + "...",
                    "receipt_check": k.check(r),
                },
                indent=2,
            )
        )
    elif args.cmd == "verify":
        spec = json.loads(open(args.spec).read())
        t = k.verify(spec)
        r = k.receipt(t)
        print(
            json.dumps(
                {
                    "triad": t.to_dict(),
                    "verdict": t.verdict(),
                    "digest": r.digest,
                    "receipt_check": k.check(r),
                },
                indent=2,
            )
        )


if __name__ == "__main__":  # pragma: no cover
    main()
