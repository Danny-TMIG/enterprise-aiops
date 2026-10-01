# DD-Long + Frequency-Phase Hopping

Two primitives, one purpose: keep a long signal from drifting.

## Double-double (DD)

A DD is a pair `(hi, lo)` of float64 values whose sum `hi + lo`
approximates an intended value with ~106 bits of mantissa instead
of 53. Constructed with Dekker's error-free transformations:

    two_sum(a, b)  -> (s, e)  with a + b = s + e, exactly
    two_prod(a, b) -> (p, e)  with a * b = p + e, exactly

Operations: `+`, `-`, `*`, `/`, `**n`. All preserve the extended
precision. `DD.from_float(x)` lifts a float64 into a DD.

## Long context

`LongAccumulator` folds a sequence of N samples into a DD sum. With
float64 the drift is O(N * eps * magnitude); with DD it is O(N *
eps²) — 30 extra bits of accuracy, which over 1M samples keeps the
last significant digit of the float64 result correct.

## Frequency-phase hopping

A `Hop` is a discrete point `(freq_index, phase_index, symbol)` in a
`16 × 16` lattice — 4 bits per hop. A `HoppingSchedule` is a
sequence of hops, each 1 ms long.

`hop_encode(payload, seed)`:
- splits the payload into 4-bit nibbles
- each nibble becomes a hop
- `freq_index` and `phase_index` are a deterministic function of
  `(symbol, seed, previous hop)` — the "hopping" pattern
- the pattern gives each hop a jitter margin: phase error up to
  `π/8` and frequency error up to one lattice step do not flip the
  symbol

`hop_decode(schedule)` inverts the transform. Lossless for
payloads `<= len(hops) * 4` bits.

## Why the two compose

A hopping schedule observed over hours accumulates phase in a
reference register. With float64 that register drifts; with DD it
does not. `DDChain` keeps the reference in DD and folds every hop's
phase into a `LongAccumulator`.

## Composition

- `app.murmur.flock.Agent` — each agent carries a `DDChain` as its
  communication layer
- `app.math.phase` — Kuramoto order `R` computed over DD phases
- `app.combinator` — a schedule is a graph; the reducer is the
  decoder
- `app.delta` — verified round-trips emit SFT pairs

## Honest limits

- The hopping codec is a demo, not a radio. Real radios add
  carrier recovery, timing recovery, and matched filtering.
- The phase-error simulation is a crude `hash`-based injector,
  not a channel model.
- DD arithmetic is ~4x slower than float64 for `+` and ~10x
  slower for `*`. Worth it when N is large.
