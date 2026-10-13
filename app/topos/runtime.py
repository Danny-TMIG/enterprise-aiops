"""Wire the topos into Mesh Seed.

The topos T is built once from the DevSkills signature plus the
concrete Mesh Seed objects (intent, spec, artifact, proof). The
Seed workflow's states map to morphisms in T; each completed run
adds arrows to T's Relational axis.
"""
from __future__ import annotations

from typing import Any

from app.topos.adjunction import construct_verify_adjunction
from app.topos.axes import Axes
from app.topos.category import Object
from app.topos.self_similar import SelfSimilarity
from app.topos.skills import SIGNATURE
from app.topos.topos import Topos


def _build_T() -> Topos:
    T = Topos("T_MeshSeed")

    # Concrete Mesh Seed objects
    T.add(Object("intent", "intent", {}))
    T.add(Object("spec", "spec", {}))
    T.add(Object("artifact", "artifact", {}))
    T.add(Object("proof", "proof", {}))

    # Forward arrows
    T.arrow("intent", "spec", "draft",
            lambda i: i if isinstance(i, dict) else {"raw": str(i)},
            meta={"axis": "F", "construct": True})
    T.arrow("spec", "artifact", "generate",
            lambda s: s,
            meta={"axis": "F", "construct": True})

    # Inverse arrows
    T.arrow("artifact", "proof", "verify",
            lambda a: {"artifact": a, "verified": True},
            meta={"axis": "G", "verify": True})

    # Relational arrows
    T.arrow("artifact", "artifact", "bind",
            lambda a: a,
            meta={"axis": "R", "binding": True})

    # The subobject classifier: which morphisms are "verified"
    T.subobject("proof", "kernel_pass",
                predicate=lambda p: isinstance(p, dict)
                and p.get("kernel_status") == "PASS")

    return T


class ToposRuntime:
    def __init__(self) -> None:
        self.T = _build_T()
        self.axes = Axes(self.T)
        self.self_sim = SelfSimilarity(self.T)
        self.adjunction = construct_verify_adjunction(
            construct=lambda i: {"artifact_of": i},
            verify=lambda a: {"proof_of": a},
        )
        self._runs: list[dict[str, Any]] = []

    # ── wiring to Mesh Seed ────────────────────────────────────
    def record_seed_run(self, wf_dict: dict[str, Any]) -> None:
        """Each completed Seed run becomes a morphism chain in T."""
        intent = wf_dict.get("intent") or {}
        spec = wf_dict.get("spec") or {}
        artifact = wf_dict.get("artifact") or {}
        kernel = wf_dict.get("kernel") or {}
        iid = f"intent:{intent.get('id', '?')}"
        sid = f"spec:{spec.get('id', '?')}"
        aid = f"artifact:{artifact.get('id', '?')}"
        pid = f"proof:{intent.get('id', '?')}"

        self.T.add(Object(iid, "intent", intent))
        self.T.add(Object(sid, "spec", spec))
        self.T.add(Object(aid, "artifact", artifact))
        self.T.add(Object(pid, "proof", kernel))

        self.T.arrow(iid, sid, f"draft:{iid}",
                     lambda _: spec, meta={"axis": "F"})
        self.T.arrow(sid, aid, f"generate:{sid}",
                     lambda _: artifact, meta={"axis": "F"})
        self.T.arrow(aid, pid, f"verify:{aid}",
                     lambda _: kernel, meta={"axis": "G"})

        self._runs.append({
            "intent": iid, "spec": sid,
            "artifact": aid, "proof": pid,
            "kernel_status": kernel.get("status"),
        })

    # ── status ─────────────────────────────────────────────────
    def status(self) -> dict[str, Any]:
        return {
            "signature": {"name": SIGNATURE["name"],
                          "count": SIGNATURE["count"]},
            "T": self.T.stats(),
            "axes": self.axes.stats(),
            "self_similar": self.self_sim.to_dict(),
            "adjunction": {
                "F ⊣ G": True,
                "triangle_left_ok": self.adjunction.triangle_left(
                    {"raw": "sample"}),
                "triangle_right_ok": self.adjunction.triangle_right(
                    {"artifact": "a"}),
            },
            "runs_recorded": len(self._runs),
        }


_RT: ToposRuntime | None = None


def get_topos() -> ToposRuntime:
    global _RT
    if _RT is None:
        _RT = ToposRuntime()
    return _RT
