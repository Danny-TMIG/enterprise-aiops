"""Algorithms as a live registry.

The markdown doc in docs/algorithms.md is a projection of this
module. Edit the data here, run the module, and the doc regenerates.

Each Algorithm carries:
    rank        1..40
    name        the algorithm
    domain      rough domain
    significance why it matters
    section     1..7 (see SECTIONS)
    level       CD level from app.cd_nand.levels (0..9)
    residuals   tuple of residual IDs from app.residual.register
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

# ── sections ────────────────────────────────────────────────────
SECTIONS: dict[int, str] = {
    1: "Foundational Algorithms",
    2: "Cryptographic & Security Algorithms",
    3: "Artificial Intelligence & Learning Algorithms",
    4: "Physics, Mathematics, and Quantum Algorithms",
    5: "Economic, Network, and Systems Algorithms",
    6: "Advanced / Modern-Era Meta Algorithms",
    7: "Meta-Historical: Algorithms That Changed Civilization",
}


# ── the algorithm record ────────────────────────────────────────
@dataclass(frozen=True)
class Algorithm:
    rank: int
    name: str
    domain: str
    significance: str
    section: int
    level: int                    # CD level 0..9
    residuals: tuple[str, ...]    # residual IDs

    def to_dict(self) -> dict:
        return asdict(self)


# ── the 40 entries ──────────────────────────────────────────────
_RAW: list[tuple] = [
    # (rank, name, domain, significance, section, level, residuals)
    (1, "Euclidean Algorithm (c. 300 BCE)", "Mathematics",
     "First known algorithm; computes greatest common divisor (GCD); "
     "defines algorithmic reasoning itself.",
     1, 0, ("M-04", "M-01")),
    (2, "Fast Fourier Transform (FFT)", "Signal Processing",
     "Converts between time and frequency domains; essential in "
     "audio, imaging, and quantum computing.",
     1, 2, ("I-02", "I-03")),
    (3, "Merge Sort / Quicksort", "Computer Science",
     "Core of data sorting and search efficiency; fundamental to "
     "database and OS design.",
     1, 1, ("C-01", "T-14")),
    (4, "Binary Search", "Algorithms & Data",
     "The archetype of divide-and-conquer; O(log n) search time.",
     1, 1, ("C-01", "T-14")),
    (5, "Dynamic Programming (Bellman)", "Optimization",
     "Basis for reinforcement learning, route planning, and "
     "sequence alignment.",
     1, 2, ("C-01", "M-21")),
    (6, "Dijkstra's Algorithm / A* Search", "Graph Theory",
     "Core of routing, GPS navigation, AI pathfinding, and network "
     "optimization.",
     1, 1, ("C-01", "T-14")),
    (7, "Backpropagation", "Machine Learning",
     "Enables deep neural networks to learn via gradient descent.",
     1, 3, ("S-01", "S-02")),
    (8, "Gradient Descent / SGD", "Optimization",
     "The most used algorithm in modern AI and data fitting.",
     1, 3, ("S-01", "M-21")),
    (9, "Monte Carlo Simulation", "Statistics & Physics",
     "Models randomness; basis of probabilistic reasoning, nuclear "
     "physics, and finance.",
     1, 3, ("I-10", "S-01")),
    (10, "Simulated Annealing", "Optimization",
     "Mimics physical cooling to find global minima; used in chip "
     "design and scheduling.",
     1, 5, ("M-21", "X-10")),

    # ── 2. Cryptographic ───────────────────────────────────────
    (11, "RSA", "Cryptography",
     "Public-key encryption; enables modern secure communication.",
     2, 2, ("K-01", "K-03")),
    (12, "Diffie–Hellman Key Exchange", "Cryptography",
     "Foundation for secure internet key exchange.",
     2, 2, ("K-01", "K-04")),
    (13, "SHA-2 / SHA-3 Hashing", "Cryptography",
     "Data integrity verification, blockchain proof-of-work.",
     2, 2, ("K-01", "K-13")),
    (14, "Elliptic Curve Cryptography (ECC)", "Cryptography",
     "Efficient encryption; used in Bitcoin, SSL, and blockchain wallets.",
     2, 2, ("K-01", "K-04")),
    (15, "Zero-Knowledge Proofs (ZKP)", "Cryptography",
     "Enables proof without revealing data; central to "
     "privacy-preserving blockchain.",
     2, 4, ("K-10", "K-11")),

    # ── 3. AI / Learning ───────────────────────────────────────
    (16, "Perceptron / Neural Networks", "AI",
     "The foundation of machine learning.",
     3, 3, ("S-01", "B-01")),
    (17, "Transformer (Attention Mechanism)", "Deep Learning",
     "Core of GPT, BERT, Gemini, Claude, etc.; enables "
     "context-rich language understanding.",
     3, 7, ("M-23", "I-02")),
    (18, "Convolutional Neural Network (CNN)", "Computer Vision",
     "Powers vision systems, autonomous vehicles, and medical imaging.",
     3, 4, ("S-01", "B-16")),
    (19, "Reinforcement Learning (Q-Learning / Policy Gradient)", "AI",
     "Agents learn via reward feedback; used in robotics and AlphaGo.",
     3, 5, ("M-21", "N-01")),
    (20, "Expectation-Maximization (EM)", "Statistics",
     "Unsupervised learning of latent variables (e.g., clustering, HMMs).",
     3, 6, ("S-06", "S-01")),

    # ── 4. Physics / Quantum ───────────────────────────────────
    (21, "Newton–Raphson Method", "Numerical Analysis",
     "Core iterative method for solving nonlinear equations.",
     4, 3, ("M-04", "K-24")),
    (22, "Fast Multipole Method (FMM)", "Computational Physics",
     "Reduces N-body problems from O(N²) to O(N); used in astrophysics.",
     4, 5, ("M-21", "C-22")),
    (23, "Shor's Algorithm", "Quantum Computing",
     "Polynomial-time factorization; threatens RSA; proves quantum "
     "supremacy.",
     4, 8, ("K-02", "M-16")),
    (24, "Grover's Algorithm", "Quantum Computing",
     "Quadratic speed-up for unstructured search.",
     4, 8, ("C-01", "M-17")),
    (25, "Simons' Algorithm", "Quantum Foundations",
     "Early quantum algorithm demonstrating exponential speed-up; "
     "precursor to Shor's.",
     4, 8, ("M-23", "C-14")),

    # ── 5. Economic / Network ──────────────────────────────────
    (26, "PageRank", "Information Retrieval",
     "Google's web ranking engine; models influence and link importance.",
     5, 6, ("D-01", "X-10")),
    (27, "Linear Programming (Simplex / Interior Point)", "Optimization",
     "Fundamental to economics, logistics, and control theory.",
     5, 5, ("M-21", "N-06")),
    (28, "Kalman Filter", "Control Systems",
     "Predicts and corrects system states; used in navigation, "
     "robotics, and finance.",
     5, 6, ("E-01", "S-04")),
    (29, "Bayesian Inference / Belief Propagation", "Probabilistic AI",
     "Backbone of probabilistic reasoning and graphical models.",
     5, 6, ("S-06", "Z-01")),
    (30, "Blockchains (Merkle Tree + Consensus)", "Distributed Systems",
     "Decentralized verification and immutable ledgers.",
     5, 7, ("D-02", "K-01")),

    # ── 6. Meta algorithms ─────────────────────────────────────
    (31, "Genetic Algorithms / Evolutionary Strategies", "Optimization",
     "Mimics evolution to optimize complex systems.",
     6, 6, ("Q-06", "M-21")),
    (32, "Swarm Optimization (Particle Swarm, Ant Colony)", "Collective AI",
     "Models emergent intelligence via distributed agents.",
     6, 6, ("X-10", "Q-02")),
    (33, "Diffusion Models (Stable Diffusion, Denoising)", "Generative AI",
     "Foundation for modern image/video generation.",
     6, 7, ("Z-12", "I-02")),
    (34, "Quantum Annealing", "Quantum Optimization",
     "Physical realization of optimization using qubit energy "
     "minimization.",
     6, 8, ("M-21", "C-14")),
    (35, "Transformer Reinforcement Architectures (LLM Swarms)", "AGI Systems",
     "Self-referential model orchestration — core of sovereign, "
     "autonomous AI networks.",
     6, 9, ("I-10", "M-04")),

    # ── 7. Meta-historical ─────────────────────────────────────
    (36, "Turing Machine", "Computation",
     "Formalized the concept of computation itself.",
     7, 3, ("M-04", "M-23")),
    (37, "Von Neumann Architecture", "Computer Design",
     "Defined all modern computer design.",
     7, 3, ("A-07", "A-13")),
    (38, "Shannon Information Theory", "Information",
     "Quantified information; foundation of communication and data "
     "compression.",
     7, 6, ("I-01", "I-03")),
    (39, "Backpropagation + Transformers Combo", "AGI Trajectory",
     "The leap to modern LLMs and AGI trajectory.",
     7, 7, ("S-01", "M-23")),
    (40, "Gerhardt TOTALITY / Quantum Arbitrage Framework", "Total Computation",
     "Unifies symbolic, quantum, and swarm logic into self-referential "
     "total computation — a candidate for the next major leap beyond "
     "Turing completeness.",
     7, 9, ("Ω", "T-38")),
]

ALGORITHMS: tuple[Algorithm, ...] = tuple(
    Algorithm(rank=r, name=n, domain=d, significance=s,
              section=sec, level=lvl, residuals=res)
    for r, n, d, s, sec, lvl, res in _RAW
)


# ── queries ─────────────────────────────────────────────────────
def by_section(section: int) -> list[Algorithm]:
    return [a for a in ALGORITHMS if a.section == section]


def by_domain(substr: str) -> list[Algorithm]:
    s = substr.lower()
    return [a for a in ALGORITHMS if s in a.domain.lower()]


def by_level(level: int) -> list[Algorithm]:
    return [a for a in ALGORITHMS if a.level == level]


def by_residual(rid: str) -> list[Algorithm]:
    return [a for a in ALGORITHMS if rid in a.residuals]


def search(substr: str) -> list[Algorithm]:
    s = substr.lower()
    return [a for a in ALGORITHMS
            if s in a.name.lower()
            or s in a.domain.lower()
            or s in a.significance.lower()]


# ── validation against the residual register ────────────────────
def validate() -> dict:
    """Every residual ID must be a valid entry in app.residual."""
    try:
        from app.residual import register as R
    except Exception as e:
        return {"ok": False, "reason": f"register not importable: {e}"}

    bad: dict[int, list[str]] = {}
    for a in ALGORITHMS:
        for rid in a.residuals:
            if not R.is_valid(rid):
                bad.setdefault(a.rank, []).append(rid)

    # checks
    ranks = [a.rank for a in ALGORITHMS]
    sections = sorted(set(a.section for a in ALGORITHMS))
    levels = sorted(set(a.level for a in ALGORITHMS))

    return {
        "ok": not bad and ranks == list(range(1, 41)),
        "count": len(ALGORITHMS),
        "ranks_contiguous": ranks == list(range(1, 41)),
        "sections_present": sections,
        "levels_present": levels,
        "invalid_residuals": bad,
    }


# ── markdown projection ────────────────────────────────────────
_LEVEL_NAMES = {
    0: "Boolean logic",
    1: "Lambda calculus",
    2: "Combinatory logic",
    3: "Turing machine",
    4: "Pi calculus",
    5: "Interaction combinators",
    6: "Cellular automata",
    7: "Category theory",
    8: "Quantum mechanics",
    9: "General computation",
}


def render_markdown() -> str:
    """Render the registry as the canonical markdown doc."""
    out: list[str] = []
    out.append("# Forty Algorithms That Changed Civilization")
    out.append("")
    out.append("A live registry. The doc is a projection of")
    out.append("`app/atlas/algorithms.py`. Edit the data in that module")
    out.append("and re-run `python3 -m app.atlas.cli` to regenerate this file.")
    out.append("")
    out.append(f"Total entries: **{len(ALGORITHMS)}** across "
               f"**{len(SECTIONS)}** sections.")
    out.append("")

    for sec in sorted(SECTIONS.keys()):
        out.append(f"## {sec}. {SECTIONS[sec]}")
        out.append("")
        out.append("| # | Algorithm | Domain | Significance | "
                   "CD Level | Residuals |")
        out.append("|---|-----------|--------|--------------|"
                   "----------|-----------|")
        for a in by_section(sec):
            lvl = f"L{a.level} {_LEVEL_NAMES.get(a.level, '?')}"
            res = ", ".join(f"`{r}`" for r in a.residuals)
            out.append(f"| {a.rank} | {a.name} | {a.domain} | "
                       f"{a.significance} | {lvl} | {res} |")
        out.append("")

    out.append("---")
    out.append("")
    out.append("## Registry queries")
    out.append("")
    out.append("The registry is importable:")
    out.append("")
    out.append("```python")
    out.append("from app.atlas.algorithms import (")
    out.append("    ALGORITHMS, by_section, by_domain, by_level,")
    out.append("    by_residual, search, validate, write_markdown,")
    out.append(")")
    out.append("")
    out.append("by_section(3)         # all AI/learning entries")
    out.append("by_level(7)           # category-theory-level entries")
    out.append("by_residual('M-04')   # every entry terminating at Halting")
    out.append("search('transformer') # substring search")
    out.append("validate()            # check residual grounding")
    out.append("write_markdown()      # regenerate docs/algorithms.md")
    out.append("```")
    out.append("")

    # level summary
    out.append("## Level summary")
    out.append("")
    out.append("| CD Level | Name | Count |")
    out.append("|----------|------|-------|")
    for lvl in range(10):
        entries = by_level(lvl)
        out.append(f"| L{lvl} | {_LEVEL_NAMES[lvl]} | {len(entries)} |")
    out.append("")

    out.append("---")
    out.append("")
    out.append("## Grounding")
    out.append("")
    out.append("Every residual ID referenced above is a valid entry")
    out.append("in `app.residual.register`. The validation result is")
    out.append("available by running `validate()`. Entry 40 terminates")
    out.append("at `Ω` (The act of proceeding), the single arity-0")
    out.append("residual in the register.")
    out.append("")
    out.append("The register's own residual — `T-38 / C-B4` — applies to")
    out.append("this document: whether its scope is complete cannot be")
    out.append("decided from inside it. Adding entry 41 is the act of")
    out.append("proceeding.")
    out.append("")

    return "\n".join(out)


def write_markdown(path: Path | None = None) -> Path:
    p = Path(path) if path else (
        Path(__file__).resolve().parent.parent.parent
        / "docs" / "algorithms.md"
    )
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render_markdown())
    return p


def run_algorithm(
name: str = "default"):
    try:
        algos = ALGORITHMS
    except NameError:
        algos = []
    for alg in algos:
        n = getattr(alg, "name", "")
        if n.lower().startswith(name.lower()):
            return alg.to_dict() if hasattr(alg, "to_dict") else alg
    return {"name": name, "status": "not_found"}

