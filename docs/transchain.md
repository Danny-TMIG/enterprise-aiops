# Trans-chain: A → Z, all depths, criss-cross, trans-all

## Alphabet

26 atoms, A..Z. For a smaller alphabet, the first n letters.

## Chain

A chain is a finite sequence of distinct letters: `A->B->C->D`.

## Depth

`depth k` = length of the chain. `P(n,k) = n!/(n-k)!` chains.

For n = 26:

| depth | count |
|-------|-------|
| 1     | 26 |
| 2     | 650 |
| 3     | 15,600 |
| 4     | 358,800 |
| 5     | 7,893,600 |
| 6     | 165,765,600 |
| 7     | 3,315,312,000 |
| 8     | 62,999,280,000 |
| ...   | ... |
| 26    | 26! ≈ 4.03 × 10^26 |
| total | Σ P(26,k) ≈ 4.03 × 10^26 |

## Criss-cross

`zigzag(c1, c2)` interleaves two chains letter by letter, deduplicating
shared letters. The set of all zigzags across all ordered pairs of
chains is `cross_all(chains)`.

## Trans-all

The prefix-extension DAG: nodes are chains, edges `c -> c+x` for
`x ∉ c`. Transitive closure: `c1 ⇝ c2` iff `c1` is a prefix of `c2`.

- nodes = total chains
- edges = `total - n` (each chain of length k has n-k extensions;
  `Σ P(n,k)(n-k) = Σ P(n,k+1) = total - n`)
- reachability from A: chains whose head is A
- reachability to Z: chains whose tail is Z
- A ⇝ Z: chains whose head is A and tail is Z

For n = 4: 64 nodes, 60 edges.

## The claim

`A`, `A→B`, `A→B→C`, ..., `A→B→...→Z` are the depth-1, depth-2,
depth-3, depth-26 chains. There are `P(26,k)` of each. The criss-cross
is the zigzag closure. The trans-all is the prefix-extension closure.
The full set is countable in closed form, generatable lazily, and
traversable without materialization. That is what "through A to Z
criss-cross trans all" means, made concrete.
