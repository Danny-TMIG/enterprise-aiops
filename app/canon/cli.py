"""Seven sins · ten commandments · book of genesis."""
from __future__ import annotations

import sys

from app.canon.commandments import audit, enumerate_commandments
from app.canon.genesis import genesis
from app.canon.sins import SIN_SPECS, detect_all, enumerate_sins
from app.residual import register as R
from app.train.core import TrainConfig
from app.train.driver import TrainDriver


def _hdr(t):
    print("=" * 74)
    print("  " + t)
    print("=" * 74)


def main():
    _hdr("seven sins — failure modes")
    for s in enumerate_sins():
        print(f"  sin {s['index']}  {s['name']:10s}  "
              f"residuals={s['residuals']}")
        print(f"    {s['description']}")
        print(f"    detection: {s['detection']}")
        print(f"    remedy:    {s['remedy']}")
    print()

    _hdr("ten commandments — risk / reward")
    for c in enumerate_commandments():
        print(f"  {c['index']:>2}. {c['statement']}")
        print(f"      risk:   {c['risk']}")
        print(f"      reward: {c['reward']}")
    print()

    _hdr("live run of the training stack")
    cfg = TrainConfig(
        kinds=["sudoku", "crossword", "rubik", "tictactoe", "gridworld"],
        difficulties=["easy", "medium", "hard"],
        puzzles_per_tile=4,
        seed=0,
        max_workers=16,
    )
    d = TrainDriver(cfg=cfg, generations=3)
    result = d.run()

    # reconstruct Runs from the driver's returns
    from app.train.core import Trainer
    t = Trainer(cfg)
    runs = [t.run_once(index=i) for i in range(3)]
    print(f"  runs: {len(runs)}")
    for r in runs:
        print(f"    run {r.index}  digest={r.digest}  "
              f"tiles={len(r.tiles)}  outcomes={len(r.outcomes)}")
    print()

    _hdr("sin detection over the runs")
    all_sins = detect_all(runs)
    from collections import Counter
    counts = Counter(s.sin for s in all_sins)
    print(f"  total sin records: {len(all_sins)}")
    for name, n in counts.most_common():
        print(f"    {name:10s} {n}")
    print()
    if all_sins:
        print("  first 6 records:")
        for s in all_sins[:6]:
            print(f"    [{s.sin:8s}] {s.subject}")
            print(f"      evidence: {s.evidence}")
            print(f"      remedy:   {s.remedy}")
    print()

    _hdr("commandment audit on each run")
    for r in runs:
        a = audit(r)
        kept = sum(1 for x in a if x["kept"])
        print(f"  run {r.index}: {kept}/{len(a)} commandments kept")
        for x in a:
            mark = "✓" if x["kept"] else "·"
            print(f"    [{mark}] {x['index']:>2}. {x['statement']}")
    print()

    _hdr("book of genesis — reconciliation")
    for r in runs:
        g = genesis(r)
        print(f"  run {r.index}  sins={g['n_sins']}  "
              f"partitions={g['n_partitions']}")
        print(f"    confession:     {g['confession_id']}")
        print(f"    separation:     {g['separation_id']}")
        print(f"    witness:        {g['witness_id']}")
        print(f"    judgment:       {g['judgment_id']}")
        print(f"    reconciliation: {g['reconciliation_id']}")
        print(f"    rest:           {g['rest_id']}")
        print(f"    recreate:       {g['recreate_id']}")
        print(f"    verdicts:       {g['verdicts']}")
        for a in g["actions"]:
            print(f"      action: {a}")
    print()

    _hdr("residual grounding check")
    used = set()
    for s in SIN_SPECS:
        used.update(s.residual_ids)
    for c in enumerate_commandments():
        used.update(c["residuals"])
    invalid = [x for x in sorted(used) if not R.is_valid(x)]
    print(f"  residuals referenced: {len(used)}")
    print(f"  invalid:             {invalid or 'none'}")
    print(f"  omega in register:   {R.is_valid('Ω')}")
    print()

    print("=" * 74)
    print("  seven sins enumerate failure.")
    print("  ten commandments constrain risk.")
    print("  genesis reconciles the residue.")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
