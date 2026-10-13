"""Publish: hop the run's digest through the ddlong codec,
fold every hop into a DD reference, and return a single bundle.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

from app.ddlong.chain import DDChain
from app.ddlong.hop import hop_decode, hop_encode
from app.train.core import Run


def _h(*p: str) -> str:
    m = hashlib.sha256()
    for s in p:
        m.update(s.encode("utf-8")); m.update(b"\x1f")
    return "sha256:" + m.hexdigest()[:16]


@dataclass
class PublishBundle:
    run_index: int
    digest: str
    hops: int
    bits: int
    duration_s: float
    decoded_ok: bool
    phase_ref_hi: float
    phase_ref_lo: float
    chain_id: str

    def to_dict(self):
        return {"run_index": self.run_index, "digest": self.digest,
                "hops": self.hops, "bits": self.bits,
                "duration_s": round(self.duration_s, 6),
                "decoded_ok": self.decoded_ok,
                "phase_ref_hi": self.phase_ref_hi,
                "phase_ref_lo": self.phase_ref_lo,
                "chain_id": self.chain_id}


def publish(run: Run, chain_id: str = "train") -> PublishBundle:
    payload = run.digest.encode()
    sched = hop_encode(payload, seed=run.index, hop_period=1e-3)
    decoded = hop_decode(sched)
    chain = DDChain(node_id=chain_id)
    for hop in sched.hops:
        chain.observe_phase(hop.phase_radians)
    return PublishBundle(
        run_index=run.index, digest=run.digest,
        hops=len(sched.hops), bits=sched.bits,
        duration_s=sched.duration_s,
        decoded_ok=(decoded == payload),
        phase_ref_hi=chain.phase_ref.hi,
        phase_ref_lo=chain.phase_ref.lo,
        chain_id=chain_id,
    )
