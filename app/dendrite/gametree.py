"""Parallel dendritic decision trees, rendered as Mermaid.

Each tree is rooted at a linguistic root word. Branching is dendritic
(2-3 children per node, matching neuron morphology). Multiple trees
are laid out in parallel in one Mermaid graph.

Node kinds
    root    the soma       — the root word
    branch  a decision     — turn/still/keep/yield applied to left/right
    spine   a terminal     — outcome leaf

Self-registers as capability `gametree`.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

# ── root words: PIE and Greek, tagged by semantic domain ──────────
ROOTS: list[dict[str, str]] = [
    {"root": "*mer-",     "lang": "PIE",   "gloss": "to die; sea",           "domain": "mortality"},
    {"root": "*men-",     "lang": "PIE",   "gloss": "to think",              "domain": "cognition"},
    {"root": "*deh₃-",    "lang": "PIE",   "gloss": "to give",               "domain": "exchange"},
    {"root": "*gʷeyh₃-",  "lang": "PIE",   "gloss": "to live",               "domain": "vitality"},
    {"root": "*weǵ-",     "lang": "PIE",   "gloss": "to be strong",          "domain": "force"},
    {"root": "*speḱ-",    "lang": "PIE",   "gloss": "to look",               "domain": "perception"},
    {"root": "*ǵneh₃-",   "lang": "PIE",   "gloss": "to know",               "domain": "knowledge"},
    {"root": "λόγος",     "lang": "Greek", "gloss": "word, reason",          "domain": "discourse"},
    {"root": "μῦθος",     "lang": "Greek", "gloss": "story, myth",           "domain": "narrative"},
    {"root": "θάλασσα",   "lang": "Greek", "gloss": "sea",                   "domain": "place"},
    {"root": "ψυχή",      "lang": "Greek", "gloss": "soul, breath",          "domain": "spirit"},
    {"root": "κρίσις",    "lang": "Greek", "gloss": "decision, judgment",    "domain": "choice"},
    {"root": "αἵρεσις",   "lang": "Greek", "gloss": "choice, taking",        "domain": "choice"},
    {"root": "ἀλήθεια",   "lang": "Greek", "gloss": "truth, unconcealment",  "domain": "truth"},
    {"root": "πλάνη",     "lang": "Greek", "gloss": "wandering, error",      "domain": "error"},
]


BRANCH_VERBS = ["turn", "still", "keep", "yield"]


# ── dendritic node ─────────────────────────────────────────────────
@dataclass
class Dendrite:
    id: str
    kind: str                       # "root" | "branch" | "spine"
    label: str
    depth: int = 0
    children: list[Dendrite] = field(default_factory=list)

    def add(self, child: Dendrite) -> None:
        self.children.append(child)


def _slug(*parts: str) -> str:
    raw = "|".join(parts)
    return "n" + hashlib.sha1(raw.encode()).hexdigest()[:8]


# ── builders ───────────────────────────────────────────────────────
def build_tree(root: dict[str, str],
               *, branching: int = 2,
               depth: int = 3,
               tree_idx: int = 0) -> Dendrite:
    """Dendritic expansion: `branching` children per node, up to `depth`.
    Leaves are spine nodes — terminal outcomes."""
    tree = Dendrite(
        id=_slug("root", root["root"], str(tree_idx)),
        kind="root",
        label=f"{root['root']} — {root['gloss']}",
    )

    def expand(node: Dendrite, level: int) -> None:
        if level >= depth:
            return
        verb = BRANCH_VERBS[level % len(BRANCH_VERBS)]
        for i in range(branching):
            side = "left" if i == 0 else "right"
            is_leaf = (level + 1 == depth)
            label = f"→ {verb} {side}" if is_leaf else f"{verb} {side}"
            child = Dendrite(
                id=_slug(node.id, verb, side, str(i)),
                kind="spine" if is_leaf else "branch",
                label=label,
                depth=level + 1,
            )
            node.add(child)
            expand(child, level + 1)

    expand(tree, 0)
    return tree


# ── mermaid renderer ───────────────────────────────────────────────
_SHAPES: dict[str, tuple[str, str]] = {
    "root":   ("((", "))"),    # circle — soma
    "branch": ("[", "]"),      # box    — decision point
    "spine":  ("([", "])"),    # stadium— terminal
}


def _shape(kind: str) -> tuple[str, str]:
    return _SHAPES.get(kind, ("[", "]"))


def to_mermaid(trees: list[tuple[Dendrite, dict[str, str]]],
               *, title: str = "Parallel Dendritic Decision Trees") -> str:
    lines: list[str] = [f"%% {title}", "flowchart LR", ""]

    for i, (tree, root) in enumerate(trees):
        sg_id = f"T{i}"
        lines.append(f"  subgraph {sg_id}[\"{root['root']} · {root['gloss']}\"]")
        lines.append("    direction TB")

        def emit(n: Dendrite, level: int = 0) -> None:
            pad = "    " + "  " * level
            op, cl = _shape(n.kind)
            lines.append(f'{pad}{n.id}{op}"{n.label}"{cl}')
            for c in n.children:
                emit(c, level + 1)
        emit(tree, 1)

        def edges(n: Dendrite, level: int = 0) -> None:
            pad = "    " + "  " * level
            for c in n.children:
                lines.append(f"{pad}{n.id} --> {c.id}")
                edges(c, level + 1)
        edges(tree, 1)

        lines.append("  end")
        lines.append("")

    lines += [
        "  classDef root   fill:#0b3d91,stroke:#ffffff,color:#ffffff,stroke-width:2px",
        "  classDef branch fill:#1f6feb,stroke:#ffffff,color:#ffffff",
        "  classDef spine  fill:#2ea043,stroke:#ffffff,color:#ffffff",
    ]

    for tree, _ in trees:
        acc: dict[str, list[str]] = {}
        def collect(n: Dendrite) -> None:
            acc.setdefault(n.kind, []).append(n.id)
            for c in n.children:
                collect(c)
        collect(tree)
        for kind, ids in acc.items():
            lines.append(f"  class {','.join(ids)} {kind}")

    return "\n".join(lines) + "\n"


# ── top-level entry ────────────────────────────────────────────────
def render(*, which: list[int] | None = None,
           branching: int = 2,
           depth: int = 3) -> str:
    """Pick trees from ROOTS by index. Default: four Greek roots
    whose semantics are decisions themselves."""
    if which is None:
        which = [7, 10, 11, 12]  # λόγος, ψυχή, κρίσις, αἵρεσις
    pairs: list[tuple[Dendrite, dict[str, str]]] = []
    for i in which:
        r = ROOTS[i]
        pairs.append((build_tree(r, branching=branching, depth=depth,
                                 tree_idx=i), r))
    return to_mermaid(pairs,
                      title="Parallel Dendritic Decision Trees — Root Words")


# ── capability ─────────────────────────────────────────────────────
def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("gametree")
    def _entry(*args: Any, **kwargs: Any) -> dict[str, Any]:
        mmd = render(
            which=kwargs.get("which"),
            branching=int(kwargs.get("branching", 2)),
            depth=int(kwargs.get("depth", 3)),
        )
        return {
            "module": "app.dendrite.gametree",
            "roots": [ROOTS[i]["root"] for i in (kwargs.get("which") or [7, 10, 11, 12])],
            "lines": mmd.count("\n"),
            "head": mmd.splitlines()[:10],
        }


_self_register()


__all__ = ["ROOTS", "Dendrite", "build_tree", "render", "to_mermaid"]
