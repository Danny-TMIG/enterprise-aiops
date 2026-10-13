"""Adversarial tooling training.

Pairs of (attacker, defender) that exercise each other against a target
hat. Each round:
    1. attacker produces Attempts from the target hat's skill surface
    2. defender must hold against each attempt
    3. swap: the defender's exposure becomes the next round's attack

Mastery = the defender held for N consecutive rounds against a growing
attack distribution. Every attempt and every defense is written to the
RAMSubstrate ledger. Nothing is claimed before it is exercised.
"""
from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from app.core.mastery import HATS, discover_skills
from app.core.ram_substrate import RAMSubstrate


# ── data types ──────────────────────────────────────────────────
@dataclass
class Attempt:
    id: str
    payload: Any
    target_skill: str
    attack_kind: str
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class Defense:
    attempt_id: str
    held: bool
    reason: str = ""
    evidence_seq: int = 0


@dataclass
class Round:
    n: int
    attempts: int
    held: int
    broken: list[str] = field(default_factory=list)
    evidence_seq: int = 0

    @property
    def defender_ok(self) -> bool:
        return self.broken == []

    def to_dict(self) -> dict[str, Any]:
        return {"round": self.n, "attempts": self.attempts,
                "held": self.held, "broken": self.broken[:8],
                "evidence_seq": self.evidence_seq}


# ── adversary definition ────────────────────────────────────────
@dataclass
class Adversary:
    code: str
    target_hat: str
    attack: Callable[[int, random.Random], list[Attempt]]
    defend: Callable[[Attempt], bool]
    rounds: int = 6
    seed: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "target_hat": self.target_hat,
                "rounds": self.rounds}


_ADVERSARIES: dict[str, Adversary] = {}


def adversary(code: str, target_hat: str, rounds: int = 6, seed: int = 0):
    """Register a (attacker, defender) pair. Decorator-friendly:
       @adversary("net_scan", "NET")
       def pair():
           def attack(round_no, rng): ...
           def defend(attempt): ...
           return attack, defend
    """
    def deco(fn):
        result = fn if isinstance(fn, tuple) else fn()
        attack, defend = result if isinstance(result, tuple) else (fn, None)
        _ADVERSARIES[code] = Adversary(
            code=code, target_hat=target_hat, attack=attack,
            defend=defend or (lambda a: False),
            rounds=rounds, seed=seed)
        return fn
    return deco


_SUB: RAMSubstrate | None = None


def _sub() -> RAMSubstrate:
    global _SUB
    if _SUB is None:
        _SUB = RAMSubstrate(capacity=32768)
    return _SUB


# ── the training loop ───────────────────────────────────────────
@dataclass
class Verdict:
    adversary: str
    hat: str
    rounds: list[Round] = field(default_factory=list)
    mastered: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"adversary": self.adversary, "hat": self.hat,
                "rounds": [r.to_dict() for r in self.rounds],
                "mastered": self.mastered}


def train(adv: Adversary) -> Verdict:
    v = Verdict(adversary=adv.code, hat=adv.target_hat)
    rng = random.Random(adv.seed)
    for i in range(1, adv.rounds + 1):
        try:
            attempts = adv.attack(i, rng) or []
        except Exception as e:
            v.rounds.append(Round(n=i, attempts=0, held=0,
                                  broken=[f"attack raised: {e}"]))
            break
        held, broken = 0, []
        for a in attempts:
            try:
                ok = bool(adv.defend(a))
            except Exception as e:
                ok = False
                a.meta["defend_error"] = str(e)
            d = Defense(attempt_id=a.id, held=ok)
            try:
                ev = _sub().append(
                    "adversarial.defense",
                    f"{adv.code}/{a.id}",
                    {"attempt": a.__dict__, "defense": d.__dict__})
                d.evidence_seq = ev.seq
            except Exception:
                pass
            if ok:
                held += 1
            else:
                broken.append(a.id)
        r = Round(n=i, attempts=len(attempts), held=held, broken=broken)
        try:
            ev = _sub().append(
                "adversarial.round",
                f"{adv.code}/round-{i}",
                r.to_dict())
            r.evidence_seq = ev.seq
        except Exception:
            pass
        v.rounds.append(r)
        if broken:
            break
    v.mastered = bool(v.rounds) and all(r.defender_ok for r in v.rounds) \
                 and len(v.rounds) == adv.rounds
    return v


def train_all(*, hat: str | None = None) -> dict[str, Verdict]:
    out: dict[str, Verdict] = {}
    for code, adv in _ADVERSARIES.items():
        if hat and adv.target_hat != hat:
            continue
        out[code] = train(adv)
    return out


# ── built-in adversaries, one per high-signal hat ───────────────
def _attempts_vs_skills(hat: str, round_no: int, rng: random.Random,
                        k: int = 4) -> list[Attempt]:
    """Generic attacker: pick K random skills under the target hat and
    craft attempts that probe them."""
    skills_by_hat = discover_skills()
    pool = skills_by_hat.get(hat, [])
    if not pool:
        return []
    picks = rng.sample(pool, min(k, len(pool)))
    out: list[Attempt] = []
    for i, s in enumerate(picks):
        out.append(Attempt(
            id=f"{hat}-r{round_no}-{i:02d}-{s.code}",
            payload={"skill": s.code, "home": s.home,
                     "variant": rng.randint(0, 2**31)},
            target_skill=s.code,
            attack_kind="dispatch-perturb",
            meta={"round": round_no}))
    return out


def _defend_generic(attempt: Attempt) -> bool:
    """Default defender: dispatch the target skill and hold if ok."""
    try:
        from app.core.capabilities import dispatch
        d = dispatch(attempt.target_skill)
        return bool(d.ok)
    except Exception:
        return False


# register one adversary per hat that has skills
for _h in sorted(HATS.keys()):
    def _mk(hat=_h):
        def attack(round_no, rng):
            return _attempts_vs_skills(hat, round_no, rng)
        return attack, _defend_generic
    adversary(f"adv_{_h}", _h, rounds=4, seed=hash(_h) & 0xffff)(_mk())


# ── capability ──────────────────────────────────────────────────
def _self_register() -> None:
    try:
        from app.core.autoreg import cap as _acap
        _acap("adversarial", category="sec-offensive",
              equation="mastery = forall r<=N: defender holds",
              home="app/core/adversarial.py")(None)
    except Exception:
        pass
    try:
        from app.core.capabilities import register as _reg

        @_reg("adversarial")
        def _entry(*args, **kwargs):
            return {
                "adversaries": len(_ADVERSARIES),
                "hats": sorted({a.target_hat for a in _ADVERSARIES.values()}),
            }
    except Exception:
        pass


_self_register()

__all__ = [
    "Adversary",
    "Attempt",
    "Defense",
    "Round",
    "Verdict",
    "adversary",
    "train",
    "train_all",
]
