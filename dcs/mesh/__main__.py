"""python -m dcs.mesh — CLI."""

import argparse
import json

from dcs.mesh.behavior import pipeline
from dcs.mesh.report import family_table, law_report, ucs_diagram, verify_report
from dcs.mesh.taxonomy import stage as get_stage


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m dcs.mesh")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("families")
    sub.add_parser("ucs")
    sub.add_parser("laws")
    sub.add_parser("verify")
    s = sub.add_parser("stage")
    s.add_argument("id")
    c = sub.add_parser("compose")
    c.add_argument("stages", nargs="+")
    a = sub.add_parser("axes")
    a.add_argument("stages", nargs="+")

    args = p.parse_args(argv)

    if args.cmd == "families":
        print(family_table())
    elif args.cmd == "ucs":
        print(ucs_diagram())
    elif args.cmd == "laws":
        print(law_report())
    elif args.cmd == "verify":
        print(verify_report())
    elif args.cmd == "stage":
        print(json.dumps(get_stage(args.id), indent=2))
    elif args.cmd == "compose":
        pl = pipeline("custom", *args.stages)
        t, r = pl.verify()
        print(
            json.dumps(
                {
                    "stages": list(pl.ids()),
                    "triad": t.to_dict(),
                    "verdict": t.verdict(),
                    "digest": r.digest,
                },
                indent=2,
            )
        )
    elif args.cmd == "axes":
        pl = pipeline("custom", *args.stages)
        print(json.dumps(pl.contract()["axes"], indent=2))


if __name__ == "__main__":
    main()
