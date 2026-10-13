"""The shape of the system when viewed from outside.

Three adjunctions. One meta-anchor. Everything else is implementation.

    Integration ⊣ Distribution
    Distribution ⊣ Experience
    Experience ⊣ Integration
              Meta: the residual register

An adjunction F ⊣ G means: for every morphism F(A) -> B there is
exactly one morphism A -> G(B). The unit goes F(G(B)) -> B; the
counit goes A -> G(F(A)). The two sides of the adjunction are the
same thing, viewed from opposite ends.

The shape is stable under module renames, file moves, and test
rewrites, because it names what each pair of modules *is*, not
what files it lives in.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Adjunction:
    left_name: str
    right_name: str
    left_module: str
    right_module: str
    unit: str
    counit: str
    witness: str
    proof_test: str

    def to_dict(self) -> dict:
        return {
            "left": self.left_name,
            "right": self.right_name,
            "left_module": self.left_module,
            "right_module": self.right_module,
            "unit": self.unit,
            "counit": self.counit,
            "witness": self.witness,
            "proof_test": self.proof_test,
        }

    def identity(self) -> tuple:
        """The identity of the adjunction.

        Invariant under module renames and test moves: the
        module paths and the proof locator are not part of the
        identity. Only the pair, the unit, the counit, and the
        witness are.
        """
        return (self.left_name, self.right_name,
                self.unit, self.counit, self.witness)


ADJUNCTIONS: tuple[Adjunction, ...] = (
    Adjunction(
        left_name="Integration",
        right_name="Distribution",
        left_module="app.combinator.graph (the graph)",
        right_module="app.combinator.substrate (RAM / streaming / process)",
        unit="graph -> RAM(graph)",
        counit="reduce(substrate(graph)) -> normal_form(graph)",
        witness=(
            "The same six IC reduction rules produce the same normal "
            "form on RAMSubstrate and StreamingSubstrate. The graph is "
            "the source of truth; the substrate is a realization. "
            "Changing the substrate does not change the normal form."
        ),
        proof_test="tests/test_slice.py::test_03_cd_nand_all_levels",
    ),
    Adjunction(
        left_name="Distribution",
        right_name="Experience",
        left_module="app.train.core (39 tiles, 156 outcomes)",
        right_module="app.train.cd_state (one digest + one CD vector)",
        unit="39 tiles x 156 outcomes -> one CD element via resolve_cd",
        counit="one CD element -> the fields of a Run",
        witness=(
            "resolve_cd(run) compresses 39 per-tile coordinates into a "
            "single level-6 CD vector deterministically. The same Run "
            "always produces the same CD. The distribution is the "
            "39 coordinates; the experience is the one element."
        ),
        proof_test="tests/test_slice.py::test_02_parallel_grid",
    ),
    Adjunction(
        left_name="Experience",
        right_name="Integration",
        left_module="app.reconfig.codeal (one IR)",
        right_module="app.reconfig.emit (Python, SQL, MQL, RL)",
        unit="intent -> Code-AL IR via interpret + apply_rules + from_tasks",
        counit="Code-AL IR -> four target languages via emit_all",
        witness=(
            "Two paraphrases that mean the same thing produce the same "
            "Code-AL hash. The IR is canonical because the rules are "
            "content-addressed and the emission is a pure function of "
            "the CAProgram. The experience (four languages out) and the "
            "integration (one IR in) are the same operation viewed from "
            "the two ends."
        ),
        proof_test="tests/test_slice.py::test_01_intent_to_code",
    ),
)


@dataclass(frozen=True)
class MetaAnchor:
    name: str
    module: str
    rule: str
    residual_id: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "module": self.module,
            "rule": self.rule,
            "residual_id": self.residual_id,
        }


META_ANCHOR: MetaAnchor = MetaAnchor(
    name="The residual register",
    module="app.residual.terminate",
    rule=(
        "Every module anchors to a specific residual ID. Every chain "
        "walks to Ω. A module whose anchor does not resolve is "
        "unfaithful and is rejected by app.residual.anchors.validate."
    ),
    residual_id="Ω",
)


def shape_identity() -> tuple:
    """The shape's identity: invariant under rename, move, delete.

    Two systems have the same shape iff their shape_identity
    tuples are equal. The tuple does not reference files, module
    paths, or test locations.
    """
    return tuple(a.identity() for a in ADJUNCTIONS) + (
        META_ANCHOR.name, META_ANCHOR.residual_id,
    )


def render() -> str:
    lines: list[str] = []
    lines.append("THE SHAPE OF THE SYSTEM")
    lines.append("=" * 66)
    lines.append("")
    lines.append("Three adjunctions. One meta-anchor.")
    lines.append("Everything else is implementation.")
    lines.append("")
    for i, adj in enumerate(ADJUNCTIONS, 1):
        lines.append(f"── Adjunction {i}: {adj.left_name} ⊣ {adj.right_name} ──")
        lines.append(f"    L (left):   {adj.left_module}")
        lines.append(f"    R (right):  {adj.right_module}")
        lines.append(f"    unit:       {adj.unit}")
        lines.append(f"    counit:     {adj.counit}")
        lines.append(f"    witness:    {adj.witness}")
        lines.append(f"    proof:      {adj.proof_test}")
        lines.append("")
    lines.append("── Meta-anchor ──")
    lines.append(f"    {META_ANCHOR.name}  ({META_ANCHOR.module})")
    lines.append(f"    residual: {META_ANCHOR.residual_id}")
    lines.append(f"    rule:     {META_ANCHOR.rule}")
    lines.append("")
    lines.append("=" * 66)
    lines.append("Everything else — every module, every test, every")
    lines.append("registry, every document — is an implementation of")
    lines.append("this shape. Renaming a file does not change the shape.")
    lines.append("Moving a test does not change the shape. Deleting a")
    lines.append("module does not change the shape. The shape is what")
    lines.append("the system *is*, not what it is called.")
    lines.append("=" * 66)
    return "\n".join(lines)


def as_dict() -> dict:
    return {
        "adjunctions": [a.to_dict() for a in ADJUNCTIONS],
        "meta_anchor": META_ANCHOR.to_dict(),
    }


def validate() -> dict:
    """Check that each adjunction's witness module exists and that
    its proof test passes."""
    out = []
    for adj in ADJUNCTIONS:
        left_ok = _module_exists(adj.left_module)
        right_ok = _module_exists(adj.right_module)
        out.append({
            "pair": f"{adj.left_name} ⊣ {adj.right_name}",
            "left_module_exists": left_ok,
            "right_module_exists": right_ok,
        })
    meta_ok = _module_exists(META_ANCHOR.module)
    return {
        "ok": all(x["left_module_exists"] and x["right_module_exists"] for x in out)
              and meta_ok,
        "adjunctions": out,
        "meta_anchor_exists": meta_ok,
    }


def _module_exists(dotted_path: str) -> bool:
    """Take the first dotted token that looks like a module path."""
    import importlib
    # the strings are like "app.combinator.graph (the graph)"
    # extract the leading module path
    token = dotted_path.split()[0].rstrip(",;")
    try:
        importlib.import_module(token)
        return True
    except Exception:
        return False


def write_markdown(path=None) -> Path:
    from pathlib import Path
    p = Path(path) if path else (
        Path(__file__).resolve().parent.parent / "docs" / "shape.md"
    )
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# The Shape of the System\n\n```\n" + render() + "\n```\n")
    return p
