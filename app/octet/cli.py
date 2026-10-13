"""Demonstrate the octet substrate dissolving the five limits."""
from __future__ import annotations

import sys

from app.octet.backrooms import Backrooms, OctetEntry
from app.octet.bypass import bypass
from app.octet.hyper import HyperDecomposer
from app.octet.intake import from_any, from_text
from app.octet.jellyfish import Bloom

FIGMA_LIKE = {
    "document": {
        "id": "abc123",
        "name": "Checkout Flow",
        "children": [
            {"id": "f1", "type": "FRAME", "name": "Cart",
             "children": [{"id": "b1", "type": "BUTTON", "name": "Pay"}]},
            {"id": "f2", "type": "FRAME", "name": "Confirmation",
             "children": []},
        ],
    },
    "components": {
        "button": {"key": "b1", "variants": ["default", "disabled"]},
    },
}


SAMPLES = [
    ("text",   "count the words in a list and store them in postgres"),
    ("figma",  FIGMA_LIKE),
    ("bytes",  b"\x01\x02\x03hello\x00"),
    ("json",   {"op": "train", "target": "mongo", "evidence": ["tests"]}),
]


def run_one(label, payload) -> None:
    print("═" * 68)
    print(f"  input: {label}")
    print("═" * 68)
    g = from_any(payload)
    print(f"  octets:       {len(g.nodes)}")
    print(f"  graph hash:   {g.hash()}")

    hd = HyperDecomposer(max_depth=4)
    hd.decompose(g)
    s = hd.summary()
    print(f"  fragments:    {s['fragments']}  terminated={s['terminated']}  "
          f"stuck={s['stuck']}  steps={s['total_steps']}")

    ng, tasks, steps, trace = bypass(g)
    print(f"  emergent:     {len(tasks)} tasks in {steps} reduction steps")
    for t in tasks[:6]:
        print(f"    {t.id:6s} {t.shape:22s} nodes={t.nodes} "
              f"span={t.value_span}")

    # residue: any active pairs with mismatched values
    residue = [nid for nid, o in ng.nodes.items() if o.kind == "G"][:0]
    stuck_ratio = 1.0 if not trace else 0.0
    print()


def main() -> int:
    for label, payload in SAMPLES:
        run_one(label, payload)

    print("═" * 68)
    print("  jellyfish on octet graph")
    print("═" * 68)
    g = from_text("count words and store them")
    bloom = Bloom(n=3, seed=11)
    bloom.seed_pulse(g)
    for t in range(8):
        bloom.tick(g)
        print(f"  tick {t}  members={len(bloom.members)}")
    print()
    for j in bloom.snapshot():
        print(f"    {j}")

    print()
    print("═" * 68)
    print("  backrooms (octet residue)")
    print("═" * 68)
    br = Backrooms()
    g = from_text("make the writing beautiful")
    ng, tasks, steps, trace = bypass(g)
    eid = br.store(OctetEntry(
        input_hash=g.hash(),
        fragment_hash=ng.hash(),
        size=len(ng.nodes),
        reason="reduction stuck: no matching values",
    ))
    print(f"  stored: {eid}")
    print(f"  count:  {len(br.all())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
