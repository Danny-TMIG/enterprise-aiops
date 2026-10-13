"""Anchor map: every module in app/ → residual IDs it terminates at.

The chain always ends at Ω. A module with no anchor is unfaithful.
"""
from __future__ import annotations

from app.residual import register as R

OMEGA = "Ω"

# module_name → [residual_id, ...]
ANCHORS: dict[str, list[str]] = {
    # ── our conversation's modules ────────────────────────────
    "app.cst":        ["T-07","T-17","T-32","T-35","T-41"],
    "app.dispatchpatchsolve":   ["Z-01","Z-10","Z-12","B-16","L-15"],
    "app.decompose":  ["Y-01","Y-07","K-27","Y-05","Z-10"],
    "app.nested":     ["M-04","M-23","I-10","I-02"],
    "app.combinator": ["M-04","C-02","C-19","M-23","K-28"],
    "app.reconfig":   ["E-09","Z-04","Z-12","C-19"],
    "app.octet":      ["M-04","I-02","M-23","Z-12"],
    "app.agency":     ["G-01","G-02","G-09","A-01","S-11","G-10"],
    "app.dominion":   ["M-04","M-20","C-19","M-21","T-15"],

    # ── prior modules ────────────────────────────────────────
    "app.math":       ["K-27","S-01","M-01"],
    "app.moat":       ["T-07","T-31","A-04"],
    "app.mesh":       ["E-01","D-01","T-25"],
    "app.murmur":     ["B-04","S-05","X-10"],
    "app.origami":    ["C-20","Y-09","T-11"],
    "app.topos":      ["K-19","K-27","Y-01","K-22"],
    "app.seed":       ["T-41","A-01","T-21"],
    "app.meta":       ["M-04","T-32","T-12","T-24"],
    "app.proof":      ["T-17","M-20","T-23"],
    "app.dispatchpatch":        ["C-19","M-20","T-11"],
    "app.proprietary":["T-12","T-13","N-01"],
    "app.autonomy":   ["X-01","X-04","X-08"],
    "app.federation": ["D-01","D-02","G-09"],
    "app.frontier":   ["M-21","M-22","T-14"],
    "app.reality":    ["T-19","T-21","H-13"],
    "app.manifold":   ["K-19","K-21"],
    "app.embedder":   ["I-02","M-18"],
    "app.mlx_omni_engine": ["T-19","T-11","P-14"],
    "app.moa_cluster":     ["M-21","M-22"],
    "app.moe_router":      ["T-24","T-14"],
    "app.status":          ["E-01","T-25"],
    "app.telemetry_worker":["T-26","P-14","T-23"],
    "app.middleware.verification": ["T-17","M-20"],
}


def anchors_for(module: str) -> list[str]:
    return list(ANCHORS.get(module, []))


def all_modules() -> list[str]:
    return sorted(ANCHORS.keys())


def validate() -> dict[str, object]:
    """Check every anchor id is a valid register entry."""
    bad: dict[str, list[str]] = {}
    for m, ids in ANCHORS.items():
        invalid = [i for i in ids if not R.is_valid(i)]
        if invalid:
            bad[m] = invalid
    # also: is Ω in the register?
    omega_ok = R.is_valid(OMEGA)
    return {
        "modules": len(ANCHORS),
        "anchors_total": sum(len(v) for v in ANCHORS.values()),
        "invalid": bad,
        "valid": not bad and omega_ok,
        "omega_in_register": omega_ok,
    }
