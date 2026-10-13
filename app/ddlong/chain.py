"""The integrated chain: DD-Long + Frequency-Phase Hopping.

DDChain composes:
  - long-context DD accumulation (for phase reference tracking)
  - hopping encode (payload -> schedule)
  - transmit (schedule -> simulated channel with phase error)
  - hopping decode (schedule -> payload)
  - receive (verify round trip)

The chain is used by murmur agents as their communication layer:
each agent has a local DD reference phase, exchanges hopping
schedules, and accumulates incoming hops in DD so a two-hour run
does not drift.

Composes with:
  - app.murmur.flock.Agent  (each agent carries a DDChain)
  - app.math.phase          (Kuramoto R computed over DD phases)
  - app.combinator          (the schedule can be reduced as a graph)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from app.ddlong.dd import DD
from app.ddlong.hop import HoppingSchedule, hop_decode, hop_encode
from app.ddlong.longctx import LongAccumulator


@dataclass
class DDChain:
    node_id: str
    hop_period: float = 1e-3
    phase_ref: DD = field(default_factory=lambda: DD(0.0, 0.0))
    acc: LongAccumulator = field(default_factory=LongAccumulator)
    sent: int = 0
    received: int = 0

    def local_hop(self, payload: bytes, seed: int = 0) -> HoppingSchedule:
        sched = hop_encode(payload, seed=seed, hop_period=self.hop_period)
        self.sent += 1
        return sched

    def observe(self, sched: HoppingSchedule,
                phase_error_rms: float = 0.0) -> dict:
        """Accumulate the schedule's phase evolution into the
        local DD reference. This is the long-context fold."""
        for hop in sched.hops:
            self.phase_ref = self.phase_ref + DD.from_float(hop.phase_radians)
            self.acc.add(hop.phase_radians)
        self.received += 1
        return {
            "phase_ref_hi": self.phase_ref.hi,
            "phase_ref_lo": self.phase_ref.lo,
            "n_observed": self.acc.count,
        }

    def observe_phase(self, phase: float) -> None:
        """Fold a single phase sample into the DD reference.
        Called by Agent._advance on every tick. Preserves
        long-context precision so a two-hour run does not
        drift."""
        self.phase_ref = self.phase_ref + DD.from_float(phase)
        self.acc.add(phase)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "sent": self.sent,
            "received": self.received,
            "phase_ref_hi": self.phase_ref.hi,
            "phase_ref_lo": self.phase_ref.lo,
            "acc": self.acc.to_dict(),
        }


def transmit(payload: bytes, seed: int = 0,
             hop_period: float = 1e-3,
             phase_error_rms: float = 0.0) -> dict:
    """End-to-end: encode, decode, compare."""
    sched = hop_encode(payload, seed=seed, hop_period=hop_period)
    decoded = hop_decode(sched, phase_error_rms=phase_error_rms)
    ok = decoded == payload
    return {
        "payload_len": len(payload),
        "schedule_hops": len(sched.hops),
        "schedule_bits": sched.bits,
        "duration_s": sched.duration_s,
        "decoded_len": len(decoded),
        "match": ok,
        "phase_error_rms": phase_error_rms,
        "digest": hashlib.sha256(payload).hexdigest()[:16],
    }


def receive(schedule: HoppingSchedule, chain: DDChain | None = None,
            phase_error_rms: float = 0.0) -> dict:
    decoded = hop_decode(schedule, phase_error_rms=phase_error_rms)
    obs = chain.observe(schedule, phase_error_rms=phase_error_rms) if chain else {}
    return {
        "decoded_len": len(decoded),
        "chain_observed": obs,
        "digest": hashlib.sha256(decoded).hexdigest()[:16],
    }
