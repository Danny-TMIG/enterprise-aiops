"""Source article → math → target module."""
from __future__ import annotations

CATALOG: list[dict[str, str]] = [
    {"source": "Connectome",
     "math": "Adjacency A, degree D, Laplacian L = D - A",
     "target": "app.mesh / app.math.graph.laplacian"},
    {"source": "Network neuroscience",
     "math": "Algebraic connectivity λ₂(L)",
     "target": "app.mesh / app.math.graph.fiedler"},
    {"source": "Connectomics",
     "math": "Modularity Q = (1/2m) Σ_ij (A_ij − k_i k_j / 2m) δ(c_i, c_j)",
     "target": "app.mesh / app.math.graph.modularity"},
    {"source": "Connectome (chain complex)",
     "math": "∂_n : C_n → C_{n−1}, H_n = ker ∂_n / im ∂_{n+1}",
     "target": "app.topos (sheaf cohomology)"},
    {"source": "Neural oscillation",
     "math": "Kuramoto order R = |1/N Σ_j e^{iθ_j}|",
     "target": "app.murmur / app.math.phase.kuramoto_R"},
    {"source": "Neural synchrony",
     "math": "Phase-locking value PLV = |1/T Σ_t e^{i(φ_a−φ_b)}|",
     "target": "app.murmur / app.math.phase.plv"},
    {"source": "Self-organizing map",
     "math": "w_i ← w_i + η h_ci (x − w_i),  h_ci = exp(−‖r_c−r_i‖²/2σ²)",
     "target": "app.murmur / app.math.som.som_update"},
    {"source": "Neuroplasticity",
     "math": "Hebbian Δw_ij = η x_i y_j",
     "target": "skipped — no firing pairs in murmur"},
    {"source": "Brain mapping",
     "math": "Bonferroni α' = α/m",
     "target": "app.meta / app.math.stats.bonferroni"},
    {"source": "Statistical parametric mapping",
     "math": "Benjamini–Hochberg FDR step-up",
     "target": "app.meta / app.math.stats.benjamini_hochberg"},
    {"source": "Brodmann area",
     "math": "Parcellation: a partition π of X",
     "target": "app.origami (grammar as parcellation)"},
    {"source": "Cortical column",
     "math": "Repeating canonical unit",
     "target": "app.origami (Production)"},
    {"source": "Encephalization quotient",
     "math": "EQ = E / S^α",
     "target": "app.seed (CPVO: outcomes / cost)"},
    {"source": "Hemodynamic response / fMRI",
     "math": "BOLD convolution with double-gamma HRF",
     "target": "skipped — no continuous-time signal"},
    {"source": "Orchestrated objective reduction",
     "math": "Quantum superposition collapse",
     "target": "skipped — speculative"},
]


def by_target(substr: str) -> list[dict[str, str]]:
    return [e for e in CATALOG if substr in e["target"]]


def active() -> list[dict[str, str]]:
    return [e for e in CATALOG if not e["target"].startswith("skipped")]
