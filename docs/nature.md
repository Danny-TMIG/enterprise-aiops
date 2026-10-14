# Layer: nature

Directory: `nature`

## Files

    nature/__init__.py
    nature/algorithms.py

## Contents

### `nature/__init__.py`

```
"""Derived algorithms from the nature catalog."""
from nature.algorithms import ALGORITHMS, step

__all__ = ["ALGORITHMS", "step"]
```
### `nature/algorithms.py`

```
"""One executable step per algorithm.

Eight are implemented. The rest are declared in data/algorithms.json
with their math and citation, awaiting implementation. The test suite
checks that every declared algorithm appears in ALGORITHMS or in
PENDING.
"""
from __future__ import annotations
import math
import random
from typing import Any


def levy_step(state: dict, params: dict, rng: random.Random) -> dict:
    alpha = params.get("alpha", 1.5)
    scale = params.get("scale", 1.0)
    u = rng.gauss(0, 1)
    v = rng.gauss(0, 1)
    phi = (math.gamma(1 + alpha) * math.sin(math.pi * alpha / 2)
           / (math.gamma((1 + alpha) / 2) * alpha * 2 ** ((alpha - 1) / 2)))
    step = scale * (u / abs(v) ** (1 / alpha)) * phi ** (1 / alpha)
    return {"x": state["x"] + step * rng.choice([-1, 1]), "n": state["n"] + 1}


def wiener_step(state: dict, params: dict, rng: random.Random) -> dict:
    sigma = params.get("sigma", 1.0)
    dt = params.get("dt", 1.0)
    return {"x": state["x"] + rng.gauss(0, sigma * math.sqrt(dt)),
            "n": state["n"] + 1}


def kuramoto_step(state: dict, params: dict, rng: random.Random) -> dict:
    K = params.get("K", 1.0)
    omega = state.get("omega", [0.0])
    dt = params.get("dt", 0.1)
    thetas = state["theta"]
    N = len(thetas)
    new = []
    for i, ti in enumerate(thetas):
        coupling = sum(math.sin(tj - ti) for tj in thetas) / N
        new.append(ti + dt * (omega[i % len(omega)] + K * coupling))
    return {"theta": new, "omega": omega, "n": state["n"] + 1}


def logistic_step(state: dict, params: dict, rng: random.Random) -> dict:
    r = params.get("r", 0.5)
    K = params.get("K", 1.0)
    dt = params.get("dt", 0.01)
    x = state["x"]
    return {"x": x + dt * r * x * (1 - x / K), "n": state["n"] + 1}


def sir_step(state: dict, params: dict, rng: random.Random) -> dict:
    beta = params.get("beta", 0.3)
    gamma = params.get("gamma", 0.1)
    dt = params.get("dt", 0.1)
    S, I, R = state["S"], state["I"], state["R"]
    N = S + I + R
    return {"S": S + dt * (-beta * S * I / N),
            "I": I + dt * (beta * S * I / N - gamma * I),
            "R": R + dt * (gamma * I), "n": state["n"] + 1}


def hebbian_update(state: dict, params: dict, rng: random.Random) -> dict:
    eta = params.get("eta", 0.01)
    x = state["x"]
    w = state["w"]
    new_w = [[w[i][j] + eta * x[i] * x[j] for j in range(len(x))]
             for i in range(len(x))]
    return {"w": new_w, "x": x, "n": state["n"] + 1}


def turing_step(state: dict, params: dict, rng: random.Random) -> dict:
    Du = params.get("Du", 0.16)
    Dv = params.get("Dv", 0.08)
    F = params.get("F", 0.035)
    k = params.get("k", 0.065)
    dt = params.get("dt", 1.0)
    u, v = state["u"], state["v"]
    rows, cols = len(u), len(u[0])
    def lap(g, i, j):
        return (g[(i-1) % rows][j] + g[(i+1) % rows][j]
                + g[i][(j-1) % cols] + g[i][(j+1) % cols] - 4 * g[i][j])
    new_u = [[0.0]*cols for _ in range(rows)]
    new_v = [[0.0]*cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            uvv = u[i][j] * v[i][j] * v[i][j]
            new_u[i][j] = u[i][j] + dt * (Du * lap(u, i, j) - uvv + F * (1 - u[i][j]))
            new_v[i][j] = v[i][j] + dt * (Dv * lap(v, i, j) + uvv - (F + k) * v[i][j])
    return {"u": new_u, "v": new_v, "n": state["n"] + 1}


def fick_step(state: dict, params: dict, rng: random.Random) -> dict:
    D = params.get("D", 0.1)
    dt = params.get("dt", 0.1)
    c = state["c"]
    n = len(c)
    new = c[:]
    for i in range(1, n - 1):
        new[i] = c[i] + D * dt * (c[i-1] - 2 * c[i] + c[i+1])
    return {"c": new, "n": state["n"] + 1}


ALGORITHMS = {
    "levy_flight_step": levy_step,
    "wiener_step": wiener_step,
    "kuramoto_step": kuramoto_step,
    "logistic_growth": logistic_step,
    "sir_step": sir_step,
    "hebbian_update": hebbian_update,
    "gray_scott_step": turing_step,
    "fick_flux": fick_step,
}

PENDING = {
    "area_restricted_search", "levy_with_gradient", "waggle_average",
    "quorum_commit", "aco_pheromone", "stigmergy_build", "tube_reinforcement",
    "boids_rule", "topological_flock", "critical_flock", "school_edge_follow",
    "cannibal_band", "pulse_coupled", "leader_coupling", "fn_integrate",
    "hh_integrate", "goodwin_oscillator", "reaction_diffusion", "bz_oregonator",
    "diffusion_limited_aggregation", "eden_model", "boundary_expansion",
    "l_system", "memory_walk", "saw_walk", "correlated_walk", "levy_walk_2d",
    "density_gate", "sigmoid_response", "lif_neuron", "toggle_switch",
    "ising_order", "habituation_step", "sensitization_step", "stdp_update",
    "negative_feedback", "predictive_control", "clonal_selection",
    "run_and_tumble", "lv_step", "gompertz_growth", "allee_growth",
    "sirs_step", "red_queen", "spatial_lv", "darcy_flow", "poiseuille_flow",
    "conservation_law", "heat_conduction", "nernst_planck", "chemostat_step",
    "osmotic_flow", "boundary_reaction",
}


def step(name: str, state: dict, params: dict, seed: int = 0) -> dict:
    if name not in ALGORITHMS:
        raise KeyError(f"unknown algorithm: {name}")
    return ALGORITHMS[name](state, params, random.Random(seed))
```
