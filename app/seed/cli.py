from __future__ import annotations

import argparse
import json
import sys

from app.seed.runtime import SeedRuntime


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="mesh-seed")
    p.add_argument("intent")
    p.add_argument("--target", default="")
    p.add_argument("--author", default="cli-user")
    p.add_argument("--approve-spec", action="store_true")
    p.add_argument("--approve-delivery", action="store_true")
    p.add_argument("--root", default=".")
    a = p.parse_args(argv)

    rt = SeedRuntime(root=a.root)
    wf = rt.start_cli(a.intent, target=a.target, author=a.author)
    wf.draft_spec()
    if a.approve_spec:
        wf.approve_spec(by=a.author, note="auto")
    else:
        print(json.dumps({"state": wf.state.value,
                          "spec": wf.spec.to_dict()}, indent=2))
        return 0
    wf.generate_artifact()
    wf.scan(root=a.root)
    wf.prove()
    wf.kernel_check()
    po = wf.emit_proof_object()
    if a.approve_delivery:
        wf.approve_delivery(by=a.author, note="auto")
        wf.merge()
    print(json.dumps({
        "state": wf.state.value,
        "proof_object_id": po.id,
        "kernel": wf.kernel_result.get("status"),
        "cpvo": wf.cpvo.totals(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
