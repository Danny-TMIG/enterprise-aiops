"""Derived weights from SI and dimensionless constants.

Two sources, no invention:

  SI_2019        exact defining constants (BIPM 2019 revision)
  DIMENSIONLESS  measured dimensionless ratios (CODATA 2022)

Each `derive(name)` returns a float computed from those. The point is
not that these are "correct" — the point is that they are reproducible,
documented, and not arbitrary. If a fabric parameter has a natural
scale, use the natural scale; if it doesn't, say so.

Self-registers as capability `weights`.
"""
from __future__ import annotations

import math
from typing import Any

# ── SI 2019 defining constants (exact by definition) ────────────────
SI_2019: dict[str, float] = {
    "c":      299_792_458.0,      # speed of light          m/s   (exact)
    "h":      6.626_070_15e-34,   # Planck constant         J s   (exact)
    "e":      1.602_176_634e-19,  # elementary charge       C     (exact)
    "k":      1.380_649e-23,      # Boltzmann constant      J/K   (exact)
    "N_A":    6.022_140_76e23,    # Avogadro constant       1/mol (exact)
    "dnu_Cs": 9_192_631_770.0,    # Cs hyperfine           Hz    (exact)
    "K_cd":   683.0,              # luminous efficacy      lm/W  (exact)
    "hbar":   1.054_571_817e-34,  # reduced Planck         J s   (derived)
    "eps0":   8.854_187_8128e-12, # vacuum permittivity    F/m   (derived)
    "mu0":    1.256_637_062_12e-6,# vacuum permeability    N/A²  (derived)
    "G":      6.674_30e-11,       # gravitational const    m³/kg/s²
    "m_e":    9.109_383_7015e-31, # electron mass          kg
    "m_p":    1.672_621_923_69e-27, # proton mass          kg
    "R":      8.314_462_618_153,  # gas constant           J/(mol·K)
}


# ── dimensionless constants (measured) ──────────────────────────────
DIMENSIONLESS: dict[str, float] = {
    "alpha":      7.297_352_5693e-3,  # fine structure constant
    "alpha_inv":  137.035_999_084,    # 1/alpha
    "alpha_s":    0.1181,             # strong coupling at M_Z
    "alpha_w":    0.0338,             # weak coupling
    "mu_pe":      1836.152_673_43,    # m_p / m_e
    "mu_pmu_e":   206.768_2830,       # m_mu / m_e
    "cosmological": 2.888e-122,       # Lambda·l_P² (order of magnitude)
    "phi":        1.618_033_988_749_895,  # golden ratio
    "pi":         3.141_592_653_589_793,
    "euler":      2.718_281_828_459_045,
    "silver":     2.414_213_562_373_095,  # 1 + sqrt(2)
    "plastic":    1.324_717_957_244_746,  # real root of x³ = x + 1
    "sqrt2":      1.414_213_562_373_095,
    "sqrt3":      1.732_050_807_568_877,
    "sqrt5":      2.236_067_977_499_790,
}


# ── derived weights, one per fabric parameter class ─────────────────
def derive(name: str) -> float:
    """Return a named derived weight. Named, documented, reproducible."""
    D = DIMENSIONLESS
    S = SI_2019

    table: dict[str, tuple[float, str]] = {
        # time-scale weights (decay, learning rate)
        "decay.alpha":        (D["alpha"],                       "fine structure constant"),
        "decay.alpha_sq":     (D["alpha"]**2,                    "alpha squared (grain)"),
        "decay.alpha_over_mu":(D["alpha"]/D["mu_pe"],            "alpha / (m_p/m_e)"),

        # hierarchical weights (branching ratios, fan-out)
        "hierarchy.phi":      (D["phi"],                         "golden ratio"),
        "hierarchy.phi_inv":  (1.0/D["phi"],                     "golden ratio inverse"),
        "hierarchy.silver":   (D["silver"],                      "silver ratio"),
        "hierarchy.plastic":  (D["plastic"],                     "plastic number"),

        # quantum grain (discretisation)
        "grain.alpha2":       (D["alpha"]**2,                    "alpha squared"),
        "grain.alpha3":       (D["alpha"]**3,                    "alpha cubed"),
        "grain.hbar":         (S["hbar"],                        "reduced Planck"),

        # causal bound (max rate)
        "bound.inv_c":        (1.0/S["c"],                       "inverse speed of light"),
        "bound.c_inv_sq":     (1.0/(S["c"]**2),                  "inverse c squared"),
        "bound.planck_time":  (math.sqrt(S["hbar"]*S["G"]/S["c"]**5), "t_P"),

        # thermal weight (rate at temperature)
        "thermal.kT_300K":    (S["k"]*300.0,                     "kT at 300 K"),
        "thermal.inv_kT":     (1.0/(S["k"]*300.0),               "1/(kT) at 300 K"),
        "thermal.R_over_N_A": (S["R"]/S["N_A"],                  "R / N_A"),

        # electromagnetic (coupling)
        "em.alpha_em":        (D["alpha"],                       "electromagnetic coupling"),
        "em.e_over_eps0":     (S["e"]/S["eps0"],                 "e / eps0"),
        "em.mu0_over_4pi":    (S["mu0"]/(4*D["pi"]),             "mu0 / 4pi"),

        # mass ratios (relative cost)
        "mass.pe":            (D["mu_pe"],                       "m_p / m_e"),
        "mass.pmu_e":         (D["mu_pmu_e"],                    "m_mu / m_e"),
        "mass.e_over_p":      (S["m_e"]/S["m_p"],                "m_e / m_p"),

        # natural units
        "natural.hbar_c":     (S["hbar"]*S["c"],                 "hbar * c"),
        "natural.alpha_hc":   (D["alpha"]*S["hbar"]*S["c"],      "alpha * hbar * c"),

        # dimensionless geometry
        "geom.pi":            (D["pi"],                          "pi"),
        "geom.euler":         (D["euler"],                       "e"),
        "geom.sqrt2":         (D["sqrt2"],                       "sqrt(2)"),
        "geom.sqrt3":         (D["sqrt3"],                       "sqrt(3)"),
        "geom.sqrt5":         (D["sqrt5"],                       "sqrt(5)"),
    }

    if name not in table:
        raise KeyError(f"unknown derived weight: {name!r}")
    return table[name][0]


def provenance(name: str) -> dict[str, Any]:
    """Where did this weight come from?"""
    val = derive(name)
    src = "constant" if name in SI_2019 or name in DIMENSIONLESS else "derived"
    return {"name": name, "value": val, "source": src}


def by_class() -> dict[str, list[str]]:
    """Weights grouped by the fabric parameter class they serve."""
    out: dict[str, list[str]] = {}
    for k in ("decay.alpha", "decay.alpha_sq", "decay.alpha_over_mu",
              "hierarchy.phi", "hierarchy.phi_inv", "hierarchy.silver",
              "hierarchy.plastic", "grain.alpha2", "grain.alpha3",
              "grain.hbar", "bound.inv_c", "bound.c_inv_sq",
              "bound.planck_time", "thermal.kT_300K", "thermal.inv_kT",
              "thermal.R_over_N_A", "em.alpha_em", "em.e_over_eps0",
              "em.mu0_over_4pi", "mass.pe", "mass.pmu_e", "mass.e_over_p",
              "natural.hbar_c", "natural.alpha_hc", "geom.pi",
              "geom.euler", "geom.sqrt2", "geom.sqrt3", "geom.sqrt5"):
        cls = k.split(".")[0]
        out.setdefault(cls, []).append(k)
    return out


# ── integration: use derived weights as fabric parameters ───────────
def physarum_params_from_constants() -> dict[str, float]:
    """Translate derived weights into PhysarumRouter parameters."""
    return {
        "delta":       derive("decay.alpha"),          # 7.297e-3 (slow decay)
        "mu":          1.0 / derive("hierarchy.phi_inv"),  # φ (nonlinearity)
        "prune_below": derive("decay.alpha_sq"),       # 5.3e-5
        "reinforce_above": derive("hierarchy.phi_inv"),# 0.618 (golden)
        "prune_window": 16,
    }


def kuramoto_K_from_constants() -> float:
    """Phase coupling strength: 1/α gives strong lock; φ gives weak lock."""
    return 1.0 / DIMENSIONLESS["alpha"] / 100.0     # ~1.37


def self_registered_entry() -> dict[str, Any]:
    return {
        "module": "app.core.weights",
        "n_si": len(SI_2019),
        "n_dimensionless": len(DIMENSIONLESS),
        "n_derived": len(by_class()),
        "sample": {k: derive(k) for k in
                   ("decay.alpha", "hierarchy.phi", "geom.pi",
                    "mass.pe", "bound.inv_c")},
    }


def _self_register() -> None:
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("weights")
    def _entry(*args: Any, **kwargs: Any) -> dict[str, Any]:
        name = kwargs.get("name") or (args[0] if args else None)
        if name:
            return provenance(name)
        return self_registered_entry()


_self_register()


__all__ = [
    "DIMENSIONLESS",
    "SI_2019",
    "by_class",
    "derive",
    "kuramoto_K_from_constants",
    "physarum_params_from_constants",
    "provenance",
]
