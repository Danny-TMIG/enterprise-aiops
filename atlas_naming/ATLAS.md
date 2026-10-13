# Criss-Cross Naming Atlas

- Files scanned: **6601**
- Unique classes: **4464**
- Unique functions: **6902**
- Unique constants: **343**
- Unique modules: **6288**
- Unique packages: **168**

## Stdlib shadow findings

### Package names that shadow stdlib

| Package | Files |
|---|---:|
| `dis` | 4 |
| `math` | 7 |
| `platform` | 13 |

### Module names that shadow stdlib

| Module | Files |
|---|---:|
| `dis` | 4 |
| `math` | 1 |
| `parser` | 2 |
| `platform` | 2 |
| `profile` | 1 |
| `re` | 1 |
| `sys` | 1 |
| `time` | 1 |

## Cross-project collisions

### classes (47 colliding names)

| Name | Projects | Occurrences |
|---|---|---:|
| `Record` | .github, 04_INTERFACING, 20_GOVERNANCE, 30_COMPUTE, 80_INTEGRATION, 95_OPERATIONS | 104 |
| `State` | 20_GOVERNANCE, app, constructors, dcs, state | 5 |
| `Decision` | app, constructors | 5 |
| `Attestation` | app, constructors, dcs | 4 |
| `Registry` | app, constructors, registry | 3 |
| `Chain` | app, dcs | 3 |
| `Envelope` | 95_OPERATIONS, constructors, dcs | 3 |
| `Sbom` | governance, mark, sovereign-bounded-matrix | 3 |
| `Manifest` | app, constructors | 3 |
| `Witness` | app, constructors | 3 |
| `Policy` | app, constructors | 3 |
| `App` | 95_OPERATIONS, sovereign-bounded-matrix, web | 3 |
| `Api` | aiops_platform, sovereign-bounded-matrix, web | 3 |
| `Intent` | app, web | 3 |
| `Run` | app, tools | 3 |
| `Migrations` | migrations, sovereign-bounded-matrix | 2 |
| `Symbol` | app, tools | 2 |
| `Mark` | mark, sovereign-bounded-matrix | 2 |
| `Daemon` | daemon, sovereign-bounded-matrix | 2 |
| `Codeql` | .github, codeql | 2 |
| `Layer` | app, dcs | 2 |
| `Certification` | app, dcs | 2 |
| `Bundle` | constructors, dcs | 2 |
| `Core` | dcs, sovereign-bounded-matrix | 2 |
| `Evidence` | constructors, dcs | 2 |
| `Receipt` | constructors, dcs | 2 |
| `FakeRun` | dcs, tools | 2 |
| `Metrics` | dcs, web | 2 |
| `License` | app, governance | 2 |
| `Audit` | daemon, sovereign-bounded-matrix | 2 |
| `Supervisor` | daemon, sovereign-bounded-matrix | 2 |
| `Spec` | app, ncf_layer | 2 |
| `Event` | app, constructors | 2 |
| `Signal` | app, constructors | 2 |
| `Outcome` | app, constructors | 2 |
| `Capability` | app, constructors | 2 |
| `PolicyError` | app, constructors | 2 |
| `Proof` | constructors, vatican | 2 |
| `EvidenceRecord` | app, constructors | 2 |
| `Certificates` | mark, sovereign-bounded-matrix | 2 |
| `Db` | aiops_platform, sovereign-bounded-matrix | 2 |
| `Grid` | 04_INTERFACING, app | 2 |
| `TrainConfig` | app, tools | 2 |
| `TrainOutcome` | app, tools | 2 |
| `TrainTile` | app, tools | 2 |
| `Trainer` | app, tools | 2 |
| `MeshOfMeshes` | app, tools | 2 |

### functions (129 colliding names)

| Name | Projects | Occurrences |
|---|---|---:|
| `digest` | .github, 04_INTERFACING, 20_GOVERNANCE, 30_COMPUTE, 80_INTEGRATION, 95_OPERATIONS | 4066 |
| `__init__` | .github, 04_INTERFACING, 20_GOVERNANCE, 30_COMPUTE, 80_INTEGRATION, 95_OPERATIONS | 241 |
| `emit` | .github, 04_INTERFACING, 20_GOVERNANCE, 30_COMPUTE, 80_INTEGRATION, 95_OPERATIONS | 109 |
| `merkle_root` | .github, 04_INTERFACING, 20_GOVERNANCE, 30_COMPUTE, 80_INTEGRATION, 95_OPERATIONS | 105 |
| `records` | .github, 04_INTERFACING, 20_GOVERNANCE, 30_COMPUTE, 80_INTEGRATION, 95_OPERATIONS | 103 |
| `to_dict` | app, auto_app, dcs, tools | 76 |
| `main` | aiops_platform, app, assign_attributes.py, auto_app, bridge, dcs | 66 |
| `verify` | app, dcs, scripts | 21 |
| `get` | app, dcs | 19 |
| `add` | app, dcs, tools | 13 |
| `register` | app, dcs | 13 |
| `_h` | app, tools | 13 |
| `__post_init__` | app, dcs | 12 |
| `render` | app, dcs | 11 |
| `validate` | app, dcs | 11 |
| `run` | _self, app, dcs | 10 |
| `stats` | app, dcs | 10 |
| `deco` | app, dcs, tools | 10 |
| `id` | app, tools | 10 |
| `step` | app, dcs, tools | 9 |
| `apply` | aiops_platform, app | 9 |
| `sign` | app, dcs, scripts | 8 |
| `__repr__` | app, dcs | 8 |
| `generate` | app, dcs, enterprise_aiops | 7 |
| `append` | app, dcs | 6 |
| `key` | app, dcs, tools | 6 |
| `summary` | app, dcs | 6 |
| `list` | app, dcs | 6 |
| `check` | app, dcs, tools | 6 |
| `visit` | app, dcs, tools | 6 |
| `is_terminal` | _self, app, dcs | 6 |
| `snapshot` | app, dcs | 6 |
| `evaluate` | app, auto_app, reality_engine.py | 5 |
| `run_all` | app, dcs, tools | 5 |
| `rate` | app, tools | 5 |
| `render_markdown` | app, dcs | 4 |
| `load` | app, dcs | 4 |
| `merge` | app, dcs | 4 |
| `mean` | app, dcs | 4 |
| `walk` | app, dcs | 4 |
| `_load` | app, dcs | 4 |
| `__len__` | app, tools | 4 |
| `_run` | app, conftest.py, dcs | 3 |
| `health_check` | app, bridge_sovereign_nexus.py, universal_platform | 3 |
| `transition` | app, constitutional_state_machine.py | 3 |
| `_sub` | app, reality_engine.py | 3 |
| `sha256_hex` | dcs, scripts | 3 |
| `alive` | app, dcs | 3 |
| `mk` | app, dcs | 3 |
| `canonical` | app, dcs | 3 |
| `report` | app, dcs | 3 |
| `close` | app, kernel | 3 |
| `health` | 95_OPERATIONS, aiops_platform, dcs | 3 |
| `parse` | app, dcs | 3 |
| `_read` | app, dcs | 3 |
| `by_class` | app, dcs | 3 |
| `call` | app, dcs | 3 |
| `__lt__` | _self, app | 3 |
| `run_once` | app, tools | 3 |
| `criss_cross` | app, tools | 3 |
| `__iter__` | app, tools | 3 |
| `acquire_lock` | app, tests | 2 |
| `release_lock` | app, tests | 2 |
| `execute` | 95_OPERATIONS, app | 2 |
| `seed` | app, scripts | 2 |
| `classify` | app, bridge | 2 |
| `invariant` | app, tests | 2 |
| `write` | dcs, scripts | 2 |
| `build` | app, scripts | 2 |
| `head` | app, dcs | 2 |
| `verify_all` | app, dcs | 2 |
| `collect` | app, dcs | 2 |
| `provenance` | app, dcs | 2 |
| `root` | aiops_platform, dcs | 2 |
| `_` | dcs, tools | 2 |
| `diff` | app, dcs | 2 |
| `load_manifest` | app, dcs | 2 |
| `_status` | app, dcs | 2 |
| `seal` | app, dcs | 2 |
| `_hash` | app, dcs | 2 |
| `verify_chain` | app, dcs | 2 |
| `simulate` | app, dcs | 2 |
| `winner` | app, dcs | 2 |
| `minimax` | app, dcs | 2 |
| `_canon` | app, dcs | 2 |
| `from_any` | app, dcs | 2 |
| `_walk` | app, dcs | 2 |
| `_reg` | app, dcs | 2 |
| `boids` | app, dcs | 2 |
| `ant_colony` | app, dcs | 2 |
| `termite_mound` | app, dcs | 2 |
| `levy_flight` | app, dcs | 2 |
| `brownian_search` | app, dcs | 2 |
| `area_restricted` | app, dcs | 2 |
| `logistic` | app, dcs | 2 |
| `lotka_volterra` | app, dcs | 2 |
| `sir` | app, dcs | 2 |
| `kuramoto` | app, dcs | 2 |
| `firefly_sync` | app, dcs | 2 |
| `fitzhugh_nagumo` | app, dcs | 2 |
| ... (29 more) | | |

### constants (31 colliding names)

| Name | Projects | Occurrences |
|---|---|---:|
| `M` | app, dcs | 1486 |
| `ROOT` | app, bridge, dcs, scripts, setup_repo.py, tests | 31 |
| `DB` | app, scripts | 10 |
| `N` | app, dcs | 6 |
| `SKIP_DIRS` | app, bridge, dcs_codeql, scripts, tools | 5 |
| `B` | app, dcs | 5 |
| `KEY` | app, dcs, dcs_codeql | 4 |
| `PASS` | app, dcs | 4 |
| `T` | app, dcs | 4 |
| `CHECKS` | dcs_codeql, tools | 3 |
| `GRAMMAR` | bridge, dcs, vatican | 3 |
| `DEFAULT` | dcs, scripts | 3 |
| `UNKNOWN` | app, dcs | 3 |
| `FAIL` | app, dcs | 3 |
| `L` | app, dcs | 3 |
| `E` | app, dcs | 3 |
| `A` | app, dcs | 3 |
| `DIRECTORIES` | scaffold_enterprise_suite.py, scaffold_matrix.py | 2 |
| `COMPONENT_RE` | bridge, vatican | 2 |
| `ENV` | app, scripts | 2 |
| `LINE_RE` | app, scripts | 2 |
| `GEN` | scripts, tools | 2 |
| `ALGOS` | app, dcs | 2 |
| `CATEGORIES` | app, dcs | 2 |
| `PY` | app, dcs | 2 |
| `WIN_LINES` | app, dcs | 2 |
| `C` | app, dcs | 2 |
| `CATALOG_PATH` | app, dcs | 2 |
| `S` | app, dcs | 2 |
| `X` | app, dcs | 2 |
| `FLOOR` | app, dcs | 2 |

### modules (56 colliding names)

| Name | Projects | Occurrences |
|---|---|---:|
| `cli` | app, auto_app, dcs | 25 |
| `registry` | app, registry | 16 |
| `app` | 95_OPERATIONS, aiops_platform, app, sovereign-bounded-matrix, universal_platform, web | 9 |
| `codeql` | .github, app, auto_app, codeql | 8 |
| `sbom` | app, governance, mark, scripts, sovereign-bounded-matrix | 8 |
| `core` | aiops_platform, app, dcs, sovereign-bounded-matrix | 7 |
| `api` | aiops_platform, app, sovereign-bounded-matrix, web | 7 |
| `mesh` | app, dcs, mesh | 6 |
| `__main__` | 95_OPERATIONS, app, dcs | 6 |
| `db` | aiops_platform, app, dcs, sovereign-bounded-matrix | 6 |
| `migrations` | app, migrations, sovereign-bounded-matrix | 5 |
| `state` | 20_GOVERNANCE, app, state | 5 |
| `evidence` | app, dcs | 5 |
| `intent` | app, web | 5 |
| `mark` | mark, sovereign-bounded-matrix | 4 |
| `daemon` | daemon, sovereign-bounded-matrix | 4 |
| `report` | app, auto_app, dcs | 4 |
| `dis` | app, dcs | 4 |
| `audit` | daemon, sovereign-bounded-matrix | 4 |
| `supervisor` | daemon, sovereign-bounded-matrix | 4 |
| `certificates` | mark, sovereign-bounded-matrix | 4 |
| `conftest` | conftest.py, dcs, tests | 3 |
| `ct` | dcs, governance | 3 |
| `kernel` | app, dcs | 3 |
| `ui` | dcs, web | 3 |
| `security` | app, dcs, sovereign-bounded-matrix | 3 |
| `axes` | app, dcs | 3 |
| `swarm` | app, auto_app | 3 |
| `policy` | app, auto_app | 3 |
| `spec` | app, ncf_layer | 3 |
| `proof` | app, vatican | 3 |
| `dashboard` | 99_COMMAND, web | 3 |
| `metrics` | app, web | 3 |
| `health` | app, web | 3 |
| `grid` | 04_INTERFACING, app | 3 |
| `convergence` | app, mesh | 2 |
| `90_PROVENANCE_AND_SUPERSEDED_ARTIFACT_INDEX` | 90_PROVENANCE_AND_SUPERSEDED_ARTIFACT_INDEX, sovereign-bounded-matrix | 2 |
| `main` | app, universal_platform | 2 |
| `00_START_HERE` | 00_START_HERE, sovereign-bounded-matrix | 2 |
| `tests` | dcs, tests | 2 |
| `test_full_coverage` | dcs, tests | 2 |
| `verify` | dcs, scripts | 2 |
| `algorithms` | app, dcs | 2 |
| `generate` | app, dcs | 2 |
| `coalesce` | app, dcs | 2 |
| `attest` | app, dcs | 2 |
| `puzzles` | app, dcs | 2 |
| `train` | app, dcs | 2 |
| `nature` | app, dcs | 2 |
| `consensus` | app, dcs | 2 |
| `dynamic` | app, dcs | 2 |
| `meta` | app, dcs | 2 |
| `privacy` | app, dcs | 2 |
| `runner` | app, auto_app | 2 |
| `config` | app, auto_app | 2 |
| `generated` | app, constructors | 2 |

### packages (20 colliding names)

| Name | Projects | Occurrences |
|---|---|---:|
| `generated` | app, constructors | 4219 |
| `tests` | dcs, tests | 1543 |
| `app` | 95_OPERATIONS, aiops_platform, app, sovereign-bounded-matrix, web | 692 |
| `core` | aiops_platform, app, dcs, sovereign-bounded-matrix | 27 |
| `codeql` | .github, app, auto_app, codeql | 24 |
| `mesh` | app, dcs, mesh | 21 |
| `api` | aiops_platform, sovereign-bounded-matrix, web | 16 |
| `proof` | app, vatican | 15 |
| `evidence` | app, dcs | 14 |
| `mark` | mark, sovereign-bounded-matrix | 13 |
| `daemon` | daemon, sovereign-bounded-matrix | 13 |
| `db` | aiops_platform, app, sovereign-bounded-matrix | 9 |
| `sbom` | governance, mark, sovereign-bounded-matrix | 7 |
| `state` | 20_GOVERNANCE, state | 6 |
| `audit` | daemon, sovereign-bounded-matrix | 5 |
| `migrations` | migrations, sovereign-bounded-matrix | 4 |
| `supervisor` | daemon, sovereign-bounded-matrix | 4 |
| `certificates` | mark, sovereign-bounded-matrix | 4 |
| `90_PROVENANCE_AND_SUPERSEDED_ARTIFACT_INDEX` | 90_PROVENANCE_AND_SUPERSEDED_ARTIFACT_INDEX, sovereign-bounded-matrix | 3 |
| `00_START_HERE` | 00_START_HERE, sovereign-bounded-matrix | 2 |
