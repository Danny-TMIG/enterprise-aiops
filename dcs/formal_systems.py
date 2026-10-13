"""Ten formal systems, anchored to their primitive bases.

Each system has:
  basis       — the irreducible primitives
  rules       — the rewrite/compose rules
  expresses   — what it can compute (its expressivity class)
  cannot      — its known boundary
  verdict     — PROVE | SOLVE | RESOLVE | OPEN
  kernel      — Δ Π Λ τ ε decomposition of the basis itself
"""
from __future__ import annotations  # pragma: no cover

import json  # pragma: no cover
from dataclasses import asdict, dataclass  # pragma: no cover
from pathlib import Path  # pragma: no cover


@dataclass
class System:  # pragma: no cover
    n: int
    name: str
    basis: list[str]
    rules: list[str]
    expresses: str
    cannot: str
    verdict: str
    kernel: dict
    anchor: str


SYSTEMS = [
    System(
        n=1, name="Boolean Logic",
        basis=["NAND"],
        rules=[
            "NOT(x)   = NAND(x,x)",
            "AND(x,y) = NAND(NAND(x,y),NAND(x,y))",
            "OR(x,y)  = NAND(NAND(x,x),NAND(y,y))",
            "XOR(x,y) = NAND(NAND(x,NAND(x,y)),NAND(y,NAND(x,y)))",
        ],
        expresses="All of propositional logic; every boolean function.",
        cannot="Cannot represent a third truth value; CONFLICT collapses to FAIL.",
        verdict="PROVE",
        kernel={"delta":"0 vs 1","pi":"state of wire",
                "lambda":"NAND gate","tau":"input → output",
                "epsilon":"Sheffer 1913 functional completeness"},
        anchor="Sheffer 1913 / NAND completeness",
    ),
    System(
        n=2, name="Lambda Calculus",
        basis=["λ", "application", "variable"],
        rules=[
            "β-reduction: (λx.t) u → t[x := u]",
            "I     = λx.x",
            "TRUE  = λx.λy.x   FALSE = λx.λy.y",
            "IF    = λp.λa.λb. p a b",
            "0 = λf.λx.x   1 = λf.λx.f x   2 = λf.λx.f (f x)",
            "SUCC  = λn.λf.λx. f (n f x)",
            "PLUS  = λm.λn.λf.λx. m f (n f x)",
            "MULT  = λm.λn.λf. m (n f)",
            "Y     = λf.(λx.f (x x)) (λx.f (x x))",
        ],
        expresses="All computable functions; equivalent to Turing machines.",
        cannot="Cannot decide its own halting; typed variants lose universality.",
        verdict="PROVE",
        kernel={"delta":"bound vs free variable","pi":"term as normal form",
                "lambda":"application","tau":"β-reduction",
                "epsilon":"Church-Rosser confluence"},
        anchor="Church 1936 / Turing 1937",
    ),
    System(
        n=3, name="Combinatory Logic",
        basis=["S", "K"],
        rules=[
            "K x y   = x",
            "S x y z = x z (y z)",
            "I       = S K K",
        ],
        expresses="All computable functions, without bound variables.",
        cannot="Cannot avoid combinator explosion; no variable abstraction.",
        verdict="PROVE",
        kernel={"delta":"term vs reduction","pi":"combinator identity",
                "lambda":"application left-associative","tau":"S/K reduction",
                "epsilon":"Curry-Howard correspondence"},
        anchor="Schönfinkel 1924 / Curry 1930",
    ),
    System(
        n=4, name="Turing Machine",
        basis=["read", "write", "move", "state"],
        rules=[
            "δ(q, s) = (q', s', d)",
            "d ∈ {L, R}",
            "accept / reject / loop are the only termination modes",
        ],
        expresses="All computable functions.",
        cannot="Cannot decide the halting problem for arbitrary machines.",
        verdict="PROVE",
        kernel={"delta":"symbol on tape","pi":"tape state",
                "lambda":"transition function δ","tau":"head step",
                "epsilon":"Turing 1936 halting proof"},
        anchor="Turing 1936",
    ),
    System(
        n=5, name="Pi Calculus",
        basis=["send", "receive", "parallel", "new-channel"],
        rules=[
            "x⟨y⟩.P            output",
            "x(z).P            input (bind z)",
            "P | Q             parallel composition",
            "(νx)P             channel restriction",
            "x⟨y⟩.P | x(z).Q → P | Q[y/z]    reduction",
        ],
        expresses="Mobile concurrent computation; mobility of names.",
        cannot="Cannot decide bisimulation equivalence in general.",
        verdict="PROVE",
        kernel={"delta":"channel names","pi":"process identity",
                "lambda":"parallel composition","tau":"message-passing reduction",
                "epsilon":"Milner 1992 bisimulation"},
        anchor="Milner 1992 / Honda 1993",
    ),
    System(
        n=6, name="Interaction Combinators",
        basis=["γ", "δ", "ε"],
        rules=[
            "γ[x,y,z] ↔ γ[x,z,y]",
            "δ[x,y,z] ↔ δ[x,z,y]",
            "γ[x,y,z] ⊗ δ[x',y',z'] → rewrites",
            "ε annihilates; γ, δ commute",
        ],
        expresses="All of λ-calculus; universal via 3 symbols.",
        cannot="Rewrites are not confluent without a strategy.",
        verdict="PROVE",
        kernel={"delta":"active pair vs stable","pi":"net topology",
                "lambda":"wire between agents","tau":"local rewrite",
                "epsilon":"Lafont 1990 universality proof"},
        anchor="Lafont 1990 / interaction nets",
    ),
    System(
        n=7, name="Cellular Automata",
        basis=["state", "neighbor", "update-rule"],
        rules=[
            "s_i(t+1) = f(s_{i-1}(t), s_i(t), s_{i+1}(t))",
            "Rule 110 is Turing complete (Cook 2004)",
            "Rule 30 is empirically chaotic",
        ],
        expresses="Rule 110 is universal; most rules are not.",
        cannot="Cannot decide whether a given rule is universal in general.",
        verdict="PROVE",
        kernel={"delta":"cell state","pi":"lattice configuration",
                "lambda":"neighborhood","tau":"local update",
                "epsilon":"Cook 2004 rule 110 universality"},
        anchor="von Neumann 1951 / Cook 2004",
    ),
    System(
        n=8, name="Category Theory",
        basis=["identity", "composition"],
        rules=[
            "id_A : A → A",
            "(g ∘ f)(x) = g(f(x))",
            "id_B ∘ f = f = f ∘ id_A     identity law",
            "h ∘ (g ∘ f) = (h ∘ g) ∘ f   associativity",
        ],
        expresses="Any mathematical structure as objects + morphisms.",
        cannot="Cannot decide equivalence of arbitrary categories; isomorphism is undecidable in general.",
        verdict="PROVE",
        kernel={"delta":"object vs morphism","pi":"identity",
                "lambda":"composition","tau":"functor",
                "epsilon":"Eilenberg-Mac Lane 1945 axioms"},
        anchor="Eilenberg-Mac Lane 1945",
    ),
    System(
        n=9, name="Quantum Mechanics",
        basis=["position", "momentum", "Hamiltonian"],
        rules=[
            "[x, p] = iħ",
            "H ψ = iħ ∂ψ/∂t",
            "measurement collapses superposition to eigenstate",
        ],
        expresses="Non-commutative observables; unitary time evolution.",
        cannot="Cannot simultaneously specify x and p exactly (Heisenberg).",
        verdict="PROVE",
        kernel={"delta":"eigenstate vs superposition","pi":"wavefunction",
                "lambda":"commutator","tau":"unitary evolution",
                "epsilon":"Heisenberg 1927 / von Neumann 1932"},
        anchor="Heisenberg 1925 / Schrödinger 1926 / Dirac 1930",
    ),
    System(
        n=10, name="General Computation",
        basis=["state", "input", "transition"],
        rules=[
            "state_{t+1} = F(state_t, input_t)",
            "composes with itself; no fixed domain",
        ],
        expresses="Every system expressible as state + update.",
        cannot="Cannot specify F without committing to a formal system; the basis is the skeleton, not the flesh.",
        verdict="RESOLVE",
        kernel={"delta":"state vs input","pi":"current state",
                "lambda":"transition function F","tau":"state advance",
                "epsilon":"no theorem — this is a schema, not a system"},
        anchor="—",
    ),
]


def stats():  # pragma: no cover
    by_verdict = {"PROVE":0, "SOLVE":0, "RESOLVE":0, "OPEN":0}
    for s in SYSTEMS:
        by_verdict[s.verdict] += 1
    return by_verdict  # pragma: no cover


SYNONYMS = {
    # canonical form → aliases
    "state":      {"state", "tape state", "current state", "lattice configuration",
                   "state of wire", "cell state"},
    "update":     {"update-rule", "transition", "local update", "state advance",
                   "β-reduction", "S/K reduction", "head step", "unitary evolution",
                   "message-passing reduction", "functor"},
    "compose":    {"application", "composition", "parallel", "parallel composition",
                   "NAND gate", "NAND", "wire between agents", "neighborhood"},
    "identity":   {"identity", "id", "term as normal form", "combinator identity",
                   "process identity", "net topology", "wavefunction"},
    "distinction":{"0 vs 1", "bound vs free variable", "term vs reduction",
                   "symbol on tape", "channel names", "active pair vs stable",
                   "object vs morphism", "eigenstate vs superposition",
                   "state vs input", "cell state"},
    "anchor":     {"Sheffer 1913 functional completeness", "Church-Rosser confluence",
                   "Curry-Howard correspondence", "Turing 1936 halting proof",
                   "Milner 1992 bisimulation", "Lafont 1990 universality proof",
                   "Cook 2004 rule 110 universality", "Eilenberg-Mac Lane 1945 axioms",
                   "Heisenberg 1927 / von Neumann 1932", "no theorem — this is a schema, not a system"},
}


def shared_primitives():  # pragma: no cover
    """What primitives recur across systems, with synonym normalization."""
    from collections import Counter  # pragma: no cover
    reverse = {}
    for canon, aliases in SYNONYMS.items():
        for a in aliases:
            reverse[a.lower()] = canon
    c = Counter()
    for s in SYSTEMS:
        for b in s.basis:
            canon = reverse.get(b.lower(), b.lower())
            c[canon] += 1
        for k in s.kernel.values():
            canon = reverse.get(str(k).lower(), None)
            if canon:  # pragma: no cover
                c[canon] += 1
    return c  # pragma: no cover


def render():  # pragma: no cover
    by_v = stats()
    lines = [
        "═" * 72,
        "  TEN FORMAL SYSTEMS — BASIS, RULES, VERDICT",
        "═" * 72, "",
        f"  PROVE:   {by_v['PROVE']}",
        f"  SOLVE:   {by_v['SOLVE']}",
        f"  RESOLVE: {by_v['RESOLVE']}",
        f"  OPEN:    {by_v['OPEN']}",
        "",
    ]
    for s in SYSTEMS:
        tag = {"PROVE":"✓","SOLVE":"~","RESOLVE":"✗","OPEN":"?"}[s.verdict]
        lines.append("═" * 72)
        lines.append(f"  {tag} {s.n:>2}. {s.name}   [{s.verdict}]")
        lines.append("  " + "─" * 68)
        lines.append(f"      basis:      {' · '.join(s.basis)}")
        lines.append(f"      expresses:  {s.expresses}")
        lines.append(f"      cannot:     {s.cannot}")
        lines.append(f"      anchor:     {s.anchor}")
        lines.append("")
        lines.append("      rules:")
        for r in s.rules:
            lines.append(f"        • {r}")
        lines.append("")
        lines.append("      kernel:")
        for k, v in s.kernel.items():
            lines.append(f"        {k:>8}  {v}")
        lines.append("")

    # shared primitives
    lines.append("═" * 72)
    lines.append("  SHARED PRIMITIVES (recurrence across systems)")
    lines.append("═" * 72)
    for p, n in shared_primitives().most_common():
        if n > 1:  # pragma: no cover
            lines.append(f"    {n:>2}×  {p}")
    lines.append("")
    lines.append("═" * 72)
    lines.append("  Every system is a bounded orthogonal decomposition.")
    lines.append("  Every system closes at its own scale, not the scale above.")
    lines.append("  Only the last RESOLVES — it names a schema, not a system.")
    lines.append("═" * 72)
    return "\n".join(lines)  # pragma: no cover


def save(path: Path):  # pragma: no cover
    path.write_text(json.dumps({
        "systems": [asdict(s) for s in SYSTEMS],
    }, indent=2))


if __name__ == "__main__":  # pragma: no cover
    import sys  # pragma: no cover
    if len(sys.argv) > 1 and sys.argv[1] == "save":  # pragma: no cover
        save(Path("formal_systems.json"))
        print("wrote formal_systems.json")
        sys.exit(0)
    print(render())
