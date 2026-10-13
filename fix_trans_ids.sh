#!/usr/bin/env bash
set -euo pipefail
cd ~/enterprise_aiops
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

python3 - <<'PY'
import ast
from pathlib import Path

p = Path("app/train/mesh.py")
src = p.read_text()
tree = ast.parse(src)
lines = src.splitlines(keepends=True)

start = end = None
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name == "trans":
        start = (node.decorator_list[0].lineno - 1) if node.decorator_list else (node.lineno - 1)
        end = node.end_lineno
        break
if start is None:
    raise SystemExit("ERROR: trans() not found")

new = '''def _run_id(run: Any, index: int) -> str:
    """Hierarchical id where ancestors are literal prefixes of descendants.

    Default scheme: index 0 -> "r", index 1 -> "r.1", index 2 -> "r.2",
    index 3 -> "r.1.1". Every later id is prefixed by "r", so a proper
    prefix closure exists. Override by setting run.id / run.run_id, or
    pass key_fn=.
    """
    for attr in ("id", "run_id"):
        v = getattr(run, attr, None)
        if isinstance(v, str) and v:
            return v
    # 0 is root; others nest under it
    if index == 0:
        return "r"
    return "r." + ".".join(str(d) for d in _digits(index))


def _digits(n: int) -> list[int]:
    # 1 -> [1], 2 -> [2], 3 -> [1,1], 4 -> [1,2], 5 -> [1,3], 6 -> [2,1] ...
    if n < 3:
        return [n]
    out: list[int] = []
    while n >= 3:
        out.append(1 + (n - 3) % 2)
        n = 1 + (n - 3) // 2
    out.append(n)
    return list(reversed(out))


def trans(runs: List[Run], key_fn: Optional[Any] = None) -> Dict[str, Any]:
    """Prefix closure over run ids.

    Default ids are hierarchical ("r", "r.1", "r.2", "r.1.1", ...) so that
    shorter ids are literal prefixes of longer ones. Override with
    key_fn(run, i) -> str, or set run.id / run.run_id.
    """
    keys: List[str] = []
    for i, r in enumerate(runs):
        k = key_fn(r, i) if key_fn is not None else _run_id(r, i)
        keys.append(str(k))

    n = len(keys)
    adj = [set() for _ in range(n)]
    edges = 0
    for i in range(n):
        for j in range(n):
            if i != j and keys[j].startswith(keys[i] + "."):
                adj[i].add(j)
                edges += 1

    reach = [set(a) for a in adj]
    for k in range(n):
        for i in range(n):
            if k in reach[i]:
                reach[i] |= reach[k]

    transitive_pairs = sum(len(r) for r in reach)
    reachable = {keys[i]: len(reach[i]) for i in range(n)}
    return {
        "edges": edges,
        "transitive_pairs": transitive_pairs,
        "reachable": reachable,
        "keys": keys,
    }
'''

src_new = "".join(lines[:start]) + new + "".join(lines[end:])
if "from typing import Optional," not in src_new and "from typing import" in src_new:
    src_new = src_new.replace("from typing import", "from typing import Optional,", 1)
p.write_text(src_new)
print("OK: trans() rewritten with hierarchical ids")
PY

python3 - <<'PY'
from app.train.core import TrainConfig, Trainer
from app.train.mesh import trans

cfg = TrainConfig(kinds=["sudoku"], difficulties=["easy"], puzzles_per_tile=1, seed=0)
tr = Trainer(cfg)
runs = [tr.run_once(index=i) for i in range(4)]

out = trans(runs)
print("keys:            ", out["keys"])
print("edges:           ", out["edges"])
print("transitive_pairs:", out["transitive_pairs"])
print("reachable:       ", out["reachable"])

# custom: explicit hierarchy so every leaf nests under r.1 or r.2
def key_fn(r, i):
    return ["r", "r.1", "r.2", "r.1.1"][i]

out2 = trans(runs, key_fn=key_fn)
print()
print("custom keys:     ", out2["keys"])
print("custom edges:    ", out2["edges"])
print("custom pairs:    ", out2["transitive_pairs"])
print("custom reachable:", out2["reachable"])
PY
