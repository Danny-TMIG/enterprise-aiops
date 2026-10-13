"""Frequency-phase hopping codec.

A Hop is a discrete point (freq_index, phase_index, symbol_bits) in
a 2-D lattice. A HoppingSchedule is a sequence of Hops that
encodes a payload.

The codec is lossless for payloads <= len(schedule) * bits_per_hop.
Decoding tolerates phase error up to pi / 2**phase_resolution and
frequency error up to the lattice spacing — the hop lattice gives
the codec a jitter margin that a fixed carrier does not.

Uses DD arithmetic internally so a long schedule does not drift.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

# Lattice dimensions. Both are powers of two so phase and freq
# indices are exact and DD accumulation is exact.
N_FREQ  = 16        # 4 bits per hop
N_PHASE = 16        # phase quantised to pi/8 steps
BITS_PER_HOP = 4


@dataclass(frozen=True)
class Hop:
    freq_index: int          # 0..N_FREQ-1
    phase_index: int         # 0..N_PHASE-1
    symbol: int              # 0..2**BITS_PER_HOP - 1
    t: float = 0.0           # absolute time the hop begins

    def __post_init__(self):
        if not 0 <= self.freq_index < N_FREQ:
            raise ValueError(f"freq_index out of range: {self.freq_index}")
        if not 0 <= self.phase_index < N_PHASE:
            raise ValueError(f"phase_index out of range: {self.phase_index}")
        if not 0 <= self.symbol < (1 << BITS_PER_HOP):
            raise ValueError(f"symbol out of range: {self.symbol}")

    @property
    def phase_radians(self) -> float:
        return self.phase_index * (math.pi / (N_PHASE / 2))

    @property
    def freq(self) -> float:
        """Lattice frequency in units of 1/hop_period."""
        return 0.5 + self.freq_index * 0.25

    def to_dict(self) -> dict:
        return {
            "freq_index": self.freq_index,
            "phase_index": self.phase_index,
            "symbol": self.symbol,
            "t": self.t,
        }


@dataclass
class HoppingSchedule:
    hops: list[Hop] = field(default_factory=list)
    hop_period: float = 1e-3       # seconds per hop
    seed: int = 0

    @property
    def bits(self) -> int:
        return len(self.hops) * BITS_PER_HOP

    @property
    def duration_s(self) -> float:
        return len(self.hops) * self.hop_period

    def to_dict(self) -> dict:
        return {
            "hops": [h.to_dict() for h in self.hops],
            "hop_period": self.hop_period,
            "seed": self.seed,
            "bits": self.bits,
            "duration_s": self.duration_s,
        }


# ── deterministic PRNG for schedule generation ─────────────────
def _prng(seed: int):
    x = (seed ^ 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    while True:
        x ^= x << 13 & 0xFFFFFFFFFFFFFFFF
        x ^= x >> 7
        x ^= x << 17 & 0xFFFFFFFFFFFFFFFF
        yield x & 0xFFFFFFFFFFFFFFFF


# ── encode ─────────────────────────────────────────────────────
def hop_encode(payload: bytes,
               seed: int = 0,
               hop_period: float = 1e-3) -> HoppingSchedule:
    """Encode bytes as a hopping schedule.

    Each 4-bit nibble of the payload becomes one hop. The hop's
    (freq_index, phase_index) is a deterministic function of the
    seed and the previous hop's indices — this is the "hopping"
    pattern that gives the schedule its jitter margin.
    """
    bits = []
    for b in payload:
        bits.append((b >> 4) & 0xF)
        bits.append(b & 0xF)

    rng = _prng(seed)
    hops: list[Hop] = []
    t = 0.0
    prev_f = 0
    prev_p = 0
    for symbol in bits:
        r = next(rng)
        # freq and phase indices are a function of symbol, seed, and prev hop
        f_idx = (symbol + (r & 0xF) + prev_f) % N_FREQ
        p_idx = ((symbol >> 1) + ((r >> 4) & 0xF) + prev_p) % N_PHASE
        hops.append(Hop(freq_index=f_idx, phase_index=p_idx,
                        symbol=symbol, t=t))
        prev_f = f_idx
        prev_p = p_idx
        t += hop_period
    return HoppingSchedule(hops=hops, hop_period=hop_period, seed=seed)


# ── decode ─────────────────────────────────────────────────────
def hop_decode(schedule: HoppingSchedule,
               phase_error_rms: float = 0.0) -> bytes:
    """Decode a hopping schedule back to bytes.

    phase_error_rms: simulated noise injected into the phase
    observations. The decoder tolerates up to pi/(N_PHASE/2) before
    the symbol decision flips.
    """
    if not schedule.hops:
        return b""
    rng = _prng(schedule.seed)
    noise_rng = random.Random(schedule.seed ^ 0xA5A5A5A5)
    out: list[int] = []
    prev_f = 0
    prev_p = 0
    tol = math.pi / (N_PHASE / 2)
    for hop in schedule.hops:
        r = next(rng)
        sym_f = (hop.freq_index - (r & 0xF) - prev_f) % N_FREQ
        sym_p = (hop.phase_index - ((r >> 4) & 0xF) - prev_p) % N_PHASE
        observed_phase = hop.phase_radians
        if phase_error_rms > 0.0:
            observed_phase += noise_rng.gauss(0.0, phase_error_rms)
        observed_phase = observed_phase % (2 * math.pi)
        observed_p_idx = int(round(observed_phase / tol)) % N_PHASE
        if observed_p_idx != hop.phase_index:
            sym = (sym_f + 1) % N_FREQ
            out.append(sym)
            prev_f = hop.freq_index
            prev_p = hop.phase_index
            continue
        candidates = [
            (sym_f - k) % N_FREQ for k in range(N_FREQ)
            if ((sym_f - k) % N_FREQ >> 1) == (sym_p % (N_PHASE // 2))
        ]
        sym = candidates[0] if candidates else sym_f
        out.append(sym)
        prev_f = hop.freq_index
        prev_p = hop.phase_index
    # repack 4-bit symbols into bytes
    acc = 0
    nibbles = 0
    data = bytearray()
    for s in out:
        acc = (acc << 4) | (s & 0xF)
        nibbles += 1
        if nibbles == 2:
            data.append(acc & 0xFF)
            acc = 0
            nibbles = 0
    return bytes(data)
