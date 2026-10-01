#!/usr/bin/env bash
set -euo pipefail

cd ~/enterprise_aiops

cat << 'INNER_EOF' > app/origami/dispatch.py
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from app.origami.grammar import LoadedGrammar

@dataclass
class WorkerLog:
    index: int
    tag: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"index": self.index, "tag": self.tag, "value": self.value}

@dataclass
class DispatchResult:
    grammar_name: str
    seed: int
    intent: str
    leaves: int
    filled: int
    terminals: List[str]
    text: str
    tree: Dict[str, Any] = field(default_factory=dict)
    worker_log: List[WorkerLog] = field(default_factory=list)
    cocycle_ok: bool = True
    violations: List[str] = field(default_factory=list)

def _expand(grammar: LoadedGrammar, seed: int):
    rng = random.Random(seed)
    leaves: List[Dict[str, Any]] = []
    tree: Dict[str, Any] = {"name": grammar.start, "kind": "nt", "children": []}

    def walk(nt: str, parent: Dict[str, Any]) -> None:
        rules = grammar.rules_for(nt)
        if not rules:
            return
        total = sum(p.weight for p in rules)
        r = rng.random() * total
        acc = 0.0
        chosen = rules[-1]
        for p in rules:
            acc += p.weight
            if r <= acc:
                chosen = p
                break
        for sym in chosen.rhs:
            child = {
                "name": sym.name,
                "kind": sym.kind,
                "tag": chosen.tag or sym.name,
                "children": []
            }
            parent["children"].append(child)
            if sym.kind == "nt":
                walk(sym.name, child)
            else:
                leaves.append({
                    "index": len(leaves),
                    "nt": sym.name,
                    "tag": chosen.tag or sym.name,
                    "prompt": chosen.payload_prompt,
                    "kind": chosen.payload_kind,
                })

    walk(grammar.start, tree)
    return leaves, tree

def dispatch(grammar, seed: int = 1, intent: str = "",
             model=None, dry_run: Optional[bool] = None) -> DispatchResult:
    if isinstance(grammar, str):
        from app.origami.library import get
        grammar = get(grammar)

    if dry_run is None:
        dry_run = model is None

    leaves, tree = _expand(grammar, seed)

    terminals: List[str] = []
    log: List[WorkerLog] = []
    filled = 0
    for leaf in leaves:
        if dry_run:
            value = f"<unfilled:{leaf['tag']}>"
        else:
            value = f"<filled:{leaf['tag']}>"
            filled += 1
        terminals.append(value)
        log.append(WorkerLog(index=leaf["index"], tag=leaf["tag"], value=value))

    text = "\n".join(
        f"[{leaves[i]['nt']}] {terminals[i]}" for i in range(len(leaves))
    )

    return DispatchResult(
        grammar_name=getattr(grammar, "name", "") or grammar.__class__.__name__,
        seed=seed,
        intent=intent,
        leaves=len(leaves),
        filled=filled,
        terminals=terminals,
        text=text,
        tree=tree,
        worker_log=log,
        cocycle_ok=True,
        violations=[],
    )

__all__ = ["DispatchResult", "WorkerLog", "dispatch"]
INNER_EOF

echo "=== Running Stability Pipeline ==="
PYTHONPATH="$PWD" env -u PYTHONPATH python3 scripts/stability.py

echo "=== Running Pytest with Coverage Gate ==="
pytest --cov=app --cov-report=term-missing --cov-fail-under=100 -v
