# Distilled mathematics from the source list

The Wikipedia listing is an index. The articles themselves carry the
mathematics. Below is the subset that maps onto existing modules in
`enterprise_aiops`, with the exact formula and the target.

## 1. Graph theory — Connectome, Connectomics, Network neuroscience

- Adjacency `A_ij`, degree `D_ii = Σ_j A_ij`, Laplacian `L = D − A`
- Algebraic connectivity `λ₂(L)` (Fiedler value): `λ₂ > 0 ⟺ connected`
- Modularity
  `Q = (1/2m) Σ_ij (A_ij − k_i k_j / 2m) δ(c_i, c_j)`
- Clustering `C`, characteristic path `L̄` (small-world summary)
- Target: `app.mesh.graph.MeshGraph`

## 2. Phase dynamics — Neural oscillation, Neural synchrony, EEG microstates

- Kuramoto order `R = |1/N Σ_j e^{iθ_j}| ∈ [0, 1]`
- Phase-locking value `PLV = |1/T Σ_t e^{i(φ_a(t) − φ_b(t))}|`
- Target: `app.murmur.flock.Flock`

## 3. Competitive learning — Self-organizing map, Neuroplasticity

- Neighborhood `h_ci(t) = exp(−‖r_c − r_i‖² / 2σ(t)²)`
- Update `w_i(t+1) = w_i(t) + η(t) h_ci(t) (x(t) − w_i(t))`
- Target: `app.murmur.agent.Agent._advance`

## 4. Multiple comparison control — Brain mapping, Statistical parametric mapping

- Bonferroni: `α' = α/m`
- Benjamini–Hochberg FDR: sort `p_(1) ≤ … ≤ p_(m)`; reject up to the
  largest `k` with `p_(k) ≤ (k/m) α`
- Target: `app.meta.loop.iterate` (currently accepts if `mean` rises — `α = 0.5`)

## 5. Parcellation — Brodmann area, Cortical column

- A parcellation `π` is a partition of a set. A map `f` commutes with `π`
  iff `f(π(x)) = π(f(x))`.
- Target: `app.origami` — grammars are parcellations of the terminal alphabet.

## 6. Homology — Connectome (as a chain complex)

- `∂_n : C_n → C_{n−1}`, `∂_{n−1} ∘ ∂_n = 0`
- `H_n = ker ∂_n / im ∂_{n+1}`
- Target: `app.topos` — the cohomological extension of the sheaf model.

## Not distilled (source has it; not applicable here)

- Hemodynamic response function and BOLD convolution — no continuous-time
  signal exists in the stack.
- Orchestrated objective reduction (Penrose) — speculative.
- Microarray / Allen Atlas gene expression — orthogonal to this codebase.
