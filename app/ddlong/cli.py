"""Demo: double-double long accumulation + frequency-phase hopping."""
from __future__ import annotations

import math
import sys

from app.ddlong.chain import DDChain, transmit
from app.ddlong.dd import DD, two_prod, two_sum
from app.ddlong.hop import BITS_PER_HOP, N_FREQ, N_PHASE
from app.ddlong.longctx import fold_sequence, phase_drift


def _hdr(t: str) -> None:
    print("=" * 68)
    print(f"  {t}")
    print("=" * 68)


def demo_dd_arithmetic() -> None:
    _hdr("double-double arithmetic")
    a = DD.from_float(1.0)
    b = DD.from_float(1e-30)
    print(f"  1.0 + 1e-30 (float64)   = {(1.0 + 1e-30)!r}")
    print(f"  1.0 + 1e-30 (DD)        = {a + b}")
    # classic: (1 + eps)^2 - 1 - 2*eps - eps^2
    eps = 1e-16
    f = (1 + eps) ** 2 - 1 - 2 * eps - eps ** 2
    dd = (DD.from_float(1.0) + DD.from_float(eps)) ** 2 \
         - DD.from_float(1.0) \
         - DD.from_float(2 * eps) \
         - DD.from_float(eps ** 2)
    print(f"  residual (float64)      = {f!r}")
    print(f"  residual (DD)           = {dd}")
    print()


def demo_two_sum_prod() -> None:
    _hdr("error-free transformations")
    a, b = 0.1, 0.2
    s, e = two_sum(a, b)
    print(f"  two_sum(0.1, 0.2)       = ({s!r}, {e!r})")
    print(f"  check: (a + b) = s + e  ->  {(a + b) == (s + e)}")
    a, b = 1e16, 3.0
    p, e = two_prod(a, b)
    print(f"  two_prod(1e16, 3.0)     = ({p!r}, {e!r})")
    print(f"  check: a * b = p + e    ->  {(a * b) == (p + e)}")
    print()


def demo_long_accumulation() -> None:
    _hdr("long-context accumulation")
    N = 1_000_000
    samples = [1.0 / (k + 1) for k in range(N)]

    # naive
    naive = 0.0
    for x in samples:
        naive += x
    # kahan (standard compensated sum)
    kahan = 0.0
    c = 0.0
    for x in samples:
        y = x - c
        t = kahan + y
        c = (t - kahan) - y
        kahan = t
    # DD
    acc = fold_sequence(samples)

    # reference: math.fsum gives the correctly-rounded sum
    import math as m
    ref = m.fsum(samples)

    print(f"  N = {N:,}")
    print(f"  naive              = {naive!r}")
    print(f"  kahan              = {kahan!r}")
    print(f"  DD  hi             = {acc.sum.hi!r}")
    print(f"  DD  lo             = {acc.sum.lo:+.6e}")
    print(f"  fsum (reference)   = {ref!r}")
    print(f"  |DD - fsum|        = {abs(acc.sum.hi - ref):.3e}")
    print(f"  |naive - fsum|     = {abs(naive - ref):.3e}")
    print()


def demo_phase_drift() -> None:
    _hdr("phase drift over a long hop sequence")
    # 1M hops of phase values
    N = 1_000_000
    phases = [(2 * math.pi * (k * 0.618033988749895 % 1.0)) for k in range(N)]
    res = phase_drift(phases)
    print(f"  N = {res['n']:,}")
    print(f"  naive sum          = {res['naive']!r}")
    print(f"  DD sum hi          = {res['dd_hi']!r}")
    print(f"  DD sum lo          = {res['dd_lo']:+.6e}")
    print(f"  residual           = {res['residual']:+.3e}")
    print(f"  residual relative  = {res['residual_rel']:.3e}")
    print()


def demo_hopping_roundtrip() -> None:
    _hdr("frequency-phase hopping codec")
    print(f"  lattice: {N_FREQ} freq x {N_PHASE} phase = {BITS_PER_HOP} bits/hop")

    payloads = [
        b"",
        b"\x01",
        b"hello",
        b"enterprise_aiops",
        bytes(range(64)),
    ]
    for p in payloads:
        r = transmit(p, seed=1)
        mark = "✓" if r["match"] else "✗"
        print(f"  [{mark}] len={r['payload_len']:3d}  "
              f"hops={r['schedule_hops']:4d}  "
              f"dur={r['duration_s']*1000:.1f}ms  "
              f"digest={r['digest']}")
    print()

    # phase error tolerance
    print("  phase-error tolerance:")
    p = b"enterprise_aiops"
    for rms in (0.0, 0.1, 0.3, 0.5, 0.7, 1.0):
        r = transmit(p, seed=1, phase_error_rms=rms)
        mark = "✓" if r["match"] else "✗"
        print(f"    rms={rms:.1f}  match={mark}")
    print()


def demo_chain() -> None:
    _hdr("integrated chain — DD reference + hopping")
    c = DDChain(node_id="murmur-a0")
    payload = b"the flock observes"
    sched = c.local_hop(payload, seed=42)
    print(f"  sent {len(payload)} bytes as {len(sched.hops)} hops")
    obs = c.observe(sched)
    print(f"  phase_ref hi = {obs['phase_ref_hi']!r}")
    print(f"  phase_ref lo = {obs['phase_ref_lo']:+.6e}")
    print(f"  observed hops = {obs['n_observed']}")
    print()
    # long run: 100k identical transmits
    c2 = DDChain(node_id="murmur-a0-long")
    payloads = [f"frame {i}".encode() for i in range(1000)]
    for i, p in enumerate(payloads):
        s = c2.local_hop(p, seed=i)
        c2.observe(s)
    print(f"  after {len(payloads)} transmits:")
    print(f"    sent        = {c2.sent}")
    print(f"    received    = {c2.received}")
    print(f"    phase_ref   = {c2.phase_ref.hi:.15g} "
          f"+ {c2.phase_ref.lo:+.3e}")
    print(f"    acc mean    = {c2.acc.mean().hi:.15g}")
    print()


def main() -> int:
    demo_dd_arithmetic()
    demo_two_sum_prod()
    demo_long_accumulation()
    demo_phase_drift()
    demo_hopping_roundtrip()
    demo_chain()
    print("=" * 68)
    print("  DD-Long + Hopping: 106-bit mantissa, discrete lattice,")
    print("  no drift over long sequences. Composes with murmur,")
    print("  math.phase, combinator.")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
