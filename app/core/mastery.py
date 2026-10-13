"""Autonomous mastery engine.

A Hat is a domain of practice (frontend, compiler, sec-offensive, ...).
A Skill is a capability that lives beneath a hat.
An Attestation records (hat, skill, probe, result, evidence_seq).

Autonomy:
    Hats  register themselves via @hat.
    Skills are DISCOVERED from autoreg.CAPABILITIES by matching the
    hat's `covers` predicate. Adding a capability to the fabric adds
    it beneath every hat whose predicate matches — no list to sync.

Mastery:
    for every (hat, skill): run the skill's probe. A skill is mastered
    iff its probe returns ok=True. The hat is mastered iff every
    discovered skill under it is mastered. Missing skills are named,
    never invented.

Ledger:
    Every probe writes one row to RAMSubstrate. The mastery state is
    recomputable from the ledger alone; nothing is cached in a way
    that can disagree with what was actually run.
"""
from __future__ import annotations

import re
import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any

from app.core import autoreg
from app.core.ram_substrate import RAMSubstrate

_LOCK = threading.RLock()


# ── data types ──────────────────────────────────────────────────
@dataclass
class Hat:
    code: str
    name: str
    covers: str              # regex against capability code or category
    description: str = ""

    def matches(self, cap_code: str, cap: dict[str, Any]) -> bool:
        hay = f"{cap_code} {cap.get('category','')} {cap.get('home','')}"
        try:
            return bool(re.search(self.covers, hay))
        except re.error:
            return False


@dataclass
class Skill:
    code: str
    hat_code: str
    category: str
    home: str
    probe: Callable[[], tuple]

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "hat": self.hat_code,
                "category": self.category, "home": self.home}


@dataclass
class Attestation:
    hat_code: str
    skill_code: str
    ok: bool
    reason: str = ""
    evidence_seq: int = 0
    when: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── registries ──────────────────────────────────────────────────
HATS: dict[str, Hat] = {}
_SKILL_PROBES: dict[str, Callable[[], tuple]] = {}


# ── decorators ──────────────────────────────────────────────────
def hat(code: str, name: str, covers: str, description: str = "") -> Callable:
    def deco(fn=None):
        with _LOCK:
            HATS[code] = Hat(code=code, name=name, covers=covers,
                             description=description)
        return fn if fn else None
    return deco


def skill(cap_code: str, probe: Callable[[], tuple]) -> None:
    """Override the default probe for a capability."""
    with _LOCK:
        _SKILL_PROBES[cap_code] = probe


# ── the 36 hats, self-registered ────────────────────────────────
# covers = regex over "cap_code category home"
HAT_TABLE = [
    ("FE",  "frontend",         "react|vue|angular|nextjs|nuxt|tailwind|material_ui|svelte|web|code_artifact|review|dense_code|code_variants|invariant|code_with_review|origami|gametree"),
    ("BE",  "backend",          "django|flask|fastapi|express|sails|api|lanes|modules|localmodel"),
    ("FS",  "fullstack",        "core|web|modules|lanes|localmodel"),
    ("MO",  "mobile",           "react_native|flutter|swift|kotlin|ios|android"),
    ("EMB", "embedded",         "arduino|esphome|zephyr|esp32|stm32|micro"),
    ("FW",  "firmware",         "firmware|bootloader|opencore|uefi|zephyr"),
    ("KRN", "kernel",           "kernel|module|syscall|driver"),
    ("SYS", "systems",          "system|proc|thread|sched|reorganize"),
    ("DIS", "distributed",      "distributed|raft|paxos|gossip|consensus|mesh|swarm"),
    ("NET", "networking",       "nmap|wireshark|tcp|udp|socket|net|pyshark|pyngrok|stem"),
    ("DB",  "database",         "sqlite|postgres|mysql|mongo|redis|cassandra|db|ram_substrate|streaming_substrate|schema"),
    ("DBA", "dba",              "migration|backup|replication|shard|index|schema"),
    ("DE",  "data-eng",         "etl|airflow|kafka|spark|flink|pipeline|modules"),
    ("DS",  "data-science",     "pandas|numpy|statsmodels|matplotlib|seaborn|scipy"),
    ("MLE", "ml-eng",           "sklearn|torch|tensorflow|transformers|peft|deepspeed|mlflow|localmodel"),
    ("RES", "research",         "research|paper|experiment|lab"),
    ("GFX", "graphics",         "opengl|vulkan|metal|shader|render|graphics|open3d"),
    ("GAME","game",             "boids|game|flocking|turing|nature_|gametree"),
    ("SHD", "shader",           "shader|glsl|hlsl|fragment|vertex"),
    ("CMP", "compiler",         "compile|parser|ast|lex|grammar|origami|nature_"),
    ("PL",  "pl-design",        "python|javascript|rust|golang|typing|lang"),
    ("FM",  "formal",           "proof|verif|invariant|lean|coq|agda|tla"),
    ("SO",  "sec-offensive",    "metasploit|nmap|zaproxy|sqlmap|exploit|sec|netsec"),
    ("SD",  "sec-defensive",    "falco|ebpf|waf|ids|filter|guard|catch_release"),
    ("CRY", "crypto",           "hmac|sha|sign|seal|key|vault|supply"),
    ("RE",  "reverse-eng",      "codeql|sarif|dissect|binja|ghidra|disasm|swarm"),
    ("SRE", "sre",              "slo|sre|reliab|stability|selfrun|observatory|mastery"),
    ("DO",  "devops",           "ansible|terraform|pulumi|jenkins|helm|argo|autoheal|regenerate"),
    ("PLT", "platform",         "k8s|kubernetes|openshift|platform|lanes"),
    ("CL",  "cloud",            "aws|gcp|azure|cloud|serverless"),
    ("REL", "release",          "release|semver|changelog|build"),
    ("QA",  "qa",               "test|pytest|hypothesis|assert|quality"),
    ("AUT", "automation",       "automation|autoheal|reorganize|regenerate|generate|modulefactory"),
    ("HPC", "hpc",              "hpc|mpi|openmp|slurm|supercomput|mesh"),
    ("SCI", "scientific",       "numpy|scipy|sympy|quant|math|phase|graph|moat"),
    ("QT",  "quantum",          "qiskit|cirq|pyquil|braket|projectq|quantum"),
    ("ROB", "robotics",         "ros2|ros|robotics|urdf|joint|bridge_ros"),
    ("SIM", "simulation",       "simulate|simulation|mock|fixture|bloch|botnet"),
    ("CAD", "cad",              "freecad|kicad|opencad|step|iges|bridge_usd"),
    ("AU",  "audio",            "audio|wav|fft|ffmpeg|whisper|sound"),
    ("VID", "video",            "video|mp4|codec|diffusers"),
    ("TW",  "tech-writer",      "docs|readme|write_markdown|shape|doc_"),
    ("DA",  "dev-advocate",     "blog|advocate|demo|cli"),
    ("SA",  "solutions-arch",   "architecture|manifold|topos|adjunction|mastery|atlas"),
    ("HW",  "hardware",         "hardware|pmc|gpio|pcie|silicon|board"),
    ("NWE", "net-eng",          "net|route|dns|firewall|nat|bridge_uns"),
    ("STE", "storage-eng",      "storage|disk|volume|s3|blob|parquet|db|data_"),
    ("CMP2","compliance",       "compliance|audit|gdpr|iso|nist|evidence|federation"),
]
for _row in HAT_TABLE:
    if len(_row) == 3:
        _code, _name, _covers = _row
        _desc = ""
    else:
        _code, _name, _covers, _desc = _row
    hat(_code, _name, _covers, _desc)()


# ── default probe for a capability ──────────────────────────────
def _default_probe(cap_code: str, cap: dict[str, Any]) -> Callable[[], tuple]:
    def probe() -> tuple:
        try:
            from app.core.capabilities import dispatch
            d = dispatch(cap_code)
            if d.ok:
                return True, "dispatch ok"
            # a probe fails honestly: unmastered is not a lie
            return False, (d.reason or "dispatch refused")[:80]
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"
    return probe


# ── discovery: map every capability to every matching hat ───────
def discover_skills() -> dict[str, list[Skill]]:
    """Walk autoreg.CAPABILITIES; for each, all hats whose regex matches."""
    with _LOCK:
        caps = dict(autoreg.CAPABILITIES)
        hats = dict(HATS)
    by_hat: dict[str, list[Skill]] = {code: [] for code in hats}
    for cap_code, cap in caps.items():
        probe = _SKILL_PROBES.get(cap_code) or _default_probe(cap_code, cap)
        for hat_code, h in hats.items():
            if h.matches(cap_code, cap):
                by_hat[hat_code].append(Skill(
                    code=cap_code, hat_code=hat_code,
                    category=str(cap.get("category", "")),
                    home=str(cap.get("home", "")),
                    probe=probe,
                ))
    return by_hat


# ── attest: probe one skill, write ledger ──────────────────────
_SUB: RAMSubstrate | None = None


def _sub() -> RAMSubstrate:
    global _SUB
    if _SUB is None:
        _SUB = RAMSubstrate(capacity=16384)
    return _SUB


def attest(skill: Skill) -> Attestation:
    try:
        ok, reason = skill.probe()
    except Exception as e:
        ok, reason = False, f"probe raised: {type(e).__name__}"
    att = Attestation(hat_code=skill.hat_code, skill_code=skill.code,
                      ok=bool(ok), reason=str(reason)[:200])
    try:
        ev = _sub().append("mastery.attest", f"{skill.hat_code}/{skill.code}",
                           att.to_dict())
        att.evidence_seq = ev.seq
    except Exception:
        pass
    return att


# ── master_autonomous: run every probe, report per hat ─────────
@dataclass
class HatReport:
    hat_code: str
    skills: int
    mastered: int
    unmastered: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.skills > 0 and self.mastered == self.skills

    def to_dict(self) -> dict[str, Any]:
        return {"hat": self.hat_code, "skills": self.skills,
                "mastered": self.mastered, "ok": self.ok,
                "unmastered": self.unmastered[:8],
                "missing": self.missing}


def master_autonomous(*, hats: list[str] | None = None) -> dict[str, HatReport]:
    """Run every skill probe under every hat. Report mastery."""
    skills_by_hat = discover_skills()
    want = set(hats) if hats else set(skills_by_hat)
    report: dict[str, HatReport] = {}
    for hat_code in sorted(want):
        skills = skills_by_hat.get(hat_code, [])
        if not skills:
            report[hat_code] = HatReport(hat_code=hat_code,
                                         skills=0, mastered=0,
                                         missing=["no capabilities matched"])
            continue
        ok_n = 0
        bad: list[str] = []
        for s in skills:
            a = attest(s)
            if a.ok:
                ok_n += 1
            else:
                bad.append(f"{s.code}: {a.reason[:60]}")
        report[hat_code] = HatReport(
            hat_code=hat_code, skills=len(skills),
            mastered=ok_n, unmastered=bad)
    return report


# ── atlas: the full map ────────────────────────────────────────
def atlas() -> dict[str, Any]:
    skills_by_hat = discover_skills()
    out: dict[str, Any] = {"hats": {}, "counts": {}}
    for hat_code, h in HATS.items():
        skills = skills_by_hat.get(hat_code, [])
        out["hats"][hat_code] = {
            "name": h.name,
            "covers": h.covers,
            "description": h.description,
            "skills": [s.to_dict() for s in skills],
            "skill_count": len(skills),
        }
    out["counts"] = {
        "hats": len(HATS),
        "skills_total": sum(len(v) for v in skills_by_hat.values()),
        "hats_with_skills": sum(1 for v in skills_by_hat.values() if v),
    }
    return out


# ── capability + self-registration ─────────────────────────────
def _self_register() -> None:
    # mirror into autoreg for the atlas side
    try:
        from app.core.autoreg import cap as _acap
        _acap("mastery", category="sre",
              equation="forall h in HATS, s in skills(h): probe(s).ok",
              home="app/core/mastery.py")(None)
    except Exception:
        pass
    # register real impl for capability dispatch / P6
    try:
        from app.core.capabilities import register as _reg

        @_reg("mastery")
        def _entry(*args, **kwargs):
            return {
                "hats": len(HATS),
                "skills_total": sum(len(v) for v in discover_skills().values()),
            }
    except Exception:
        pass


_self_register()

__all__ = [
    "HATS",
    "Attestation",
    "Hat",
    "HatReport",
    "Skill",
    "atlas",
    "attest",
    "discover_skills",
    "hat",
    "master_autonomous",
    "skill",
]
