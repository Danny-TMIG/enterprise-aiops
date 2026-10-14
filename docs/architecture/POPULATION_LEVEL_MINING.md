# Population-Level Mining

## Problem shift

Repository-level mining yields local invariants. Population-level mining yields distributional priors. The unit of evidence changes from "this team does X" to "teams like this do X with probability p."

## Data sources

- GH Archive: public event stream since 2011, petabytes total
- gharc: hourly filter to Parquet, under 100 MB peak disk
- HuggingFace 40M repos: stars, forks, language, license, size

Compression ratio, measured: 6-hour window filtered to apache/spark yields 53 KB from 1.2 GB (22,000:1).

## Population invariants

- Co-change: schema.ts to migration in 94 percent of repos
- Failure/recovery: refactor plus behavior breaks git bisect at rate R
- Phase transitions: first N commits predict trajectory

## Temporal logic mining

- Texada: 50k events at minconf 0.7 in about 300s
- ASPecMine: 50k events in under 60s
- code-maat-python: temporal coupling

Three LTL patterns:

    G(x -> XF y)
    Fy -> (not y U x)
    G(x -> G(not y))

## Pipeline

1. Extract with gharc or PyDriller
2. Normalize: encode paths, drop single-file and extra-long commits
3. Mine with Texada or ASPecMine
4. Validate on holdout: Invariant Stability meta-rule

## Insight

Local invariants from one repo. Distributional priors from all of GitHub. Codegen conditioned on what happens at scale.
