# Naming Decision Table

Fill the Decision column with one of:
`consolidate` `alias` `leave` `rename-shadow`

| Name | Occurrences | Equivalence | Decision |
|---|---:|---|---|
| `Record` | 20 | identical | |
| `State` | 5 | partial-overlap | |
| `Decision` | 5 | all-different | |
| `Attestation` | 4 | all-different | |
| `Registry` | 3 | all-different | |
| `Chain` | 3 | all-different | |
| `Envelope` | 3 | all-different | |
| `Sbom` | 3 | identical | |
| `Manifest` | 3 | all-different | |
| `Witness` | 3 | all-different | |
| `Policy` | 3 | all-different | |
| `App` | 3 | identical | |
| `Api` | 3 | identical | |
| `Intent` | 3 | partial-overlap | |
| `Run` | 3 | partial-overlap | |
| `Migrations` | 2 | identical | |
| `Symbol` | 2 | all-different | |
| `Mark` | 2 | identical | |
| `Daemon` | 2 | identical | |
| `Codeql` | 2 | identical | |
| `Layer` | 2 | all-different | |
| `Certification` | 2 | all-different | |
| `Bundle` | 2 | all-different | |
| `Core` | 2 | identical | |
| `Evidence` | 2 | all-different | |
| `Receipt` | 2 | all-different | |
| `Metrics` | 2 | all-different | |
| `License` | 2 | all-different | |
| `Audit` | 2 | identical | |
| `Supervisor` | 2 | identical | |
| `Spec` | 2 | all-different | |
| `Event` | 2 | all-different | |
| `Signal` | 2 | all-different | |
| `Outcome` | 2 | all-different | |
| `Capability` | 2 | all-different | |
| `PolicyError` | 2 | all-different | |
| `Proof` | 2 | all-different | |
| `EvidenceRecord` | 2 | all-different | |
| `Certificates` | 2 | identical | |
| `Db` | 2 | identical | |
| `Grid` | 2 | all-different | |
| `TrainConfig` | 2 | identical | |
| `TrainOutcome` | 2 | identical | |
| `TrainTile` | 2 | identical | |
| `Trainer` | 2 | identical | |
| `MeshOfMeshes` | 2 | identical | |

## `Record` — identical

- `.github/codeql/codeql.py` — hash `38f96f5d81fd3bbb`
- `.github/workflows/workflows.py` — hash `38f96f5d81fd3bbb`
- `04_INTERFACING/grid/grid.py` — hash `38f96f5d81fd3bbb`
- `20_GOVERNANCE/state/state.py` — hash `38f96f5d81fd3bbb`
- `30_COMPUTE/mlx_bridge/mlx_bridge.py` — hash `38f96f5d81fd3bbb`
- `80_INTEGRATION/wire/wire.py` — hash `38f96f5d81fd3bbb`
- `95_OPERATIONS/app/app.py` — hash `38f96f5d81fd3bbb`
- `99_COMMAND/tui/tui.py` — hash `38f96f5d81fd3bbb`
- `_self/_self.py` — hash `38f96f5d81fd3bbb`
- `_self/ql/ql.py` — hash `38f96f5d81fd3bbb`
- `aiops_platform/aiops_platform.py` — hash `38f96f5d81fd3bbb`
- `aiops_platform/app/api/api.py` — hash `38f96f5d81fd3bbb`
- `aiops_platform/app/db/db.py` — hash `38f96f5d81fd3bbb`
- `app/autonomy/policies/policies.py` — hash `38f96f5d81fd3bbb`
- `app/dis/dis.py` — hash `38f96f5d81fd3bbb`
- `app/lanes/lanes.py` — hash `38f96f5d81fd3bbb`
- `asm/asm.py` — hash `38f96f5d81fd3bbb`
- `auto_app/auto_app.py` — hash `38f96f5d81fd3bbb`
- `clickhouse_config/clickhouse_config.py` — hash `38f96f5d81fd3bbb`
- `codeql/codeql.py` — hash `38f96f5d81fd3bbb`

## `State` — partial-overlap

- `20_GOVERNANCE/state/state.py` — hash `05cfe06c9865a46c`
- `app/core/state_machine.py` — hash `d2c34f7cd7ae4088`
- `constructors/generated/State.py` — hash `2840e9d7127e33ef`
- `dcs/apop.py` — hash `6197696c252f12d3`
- `state/state.py` — hash `05cfe06c9865a46c`

## `Decision` — all-different

- `app/agency/gate.py` — hash `f1af06aff139d68c`
- `app/autonomy/__init__.py` — hash `16f5e7e7232a1530`
- `app/autonomy/decisions.py` — hash `8225a9a5f76e50a3`
- `app/murmur/state.py` — hash `fa03353bdd8a630b`
- `constructors/generated/Decision.py` — hash `2d00747ee9bf8805`

## `Attestation` — all-different

- `app/core/mastery.py` — hash `04309b7b57e71af5`
- `constructors/generated/Attestation.py` — hash `ee1ae1f9bf64705d`
- `dcs/rogue.py` — hash `2abb0131ae91482f`
- `dcs/sources/__init__.py` — hash `159854e3ed06995b`

## `Registry` — all-different

- `app/agency/registry.py` — hash `840cb0c568913377`
- `constructors/generated/Registry.py` — hash `fff3ff3f52e7b89a`
- `registry/registry.py` — hash `50fab7bcd2aa56d3`

## `Chain` — all-different

- `app/residual/terminate.py` — hash `74de00c9b20edaf8`
- `app/transchain/chain.py` — hash `35dce12cd739db8e`
- `dcs/rogue.py` — hash `3e907526cedeb5d9`

## `Envelope` — all-different

- `95_OPERATIONS/app/__main__.py` — hash `ac896aea1520a805`
- `constructors/generated/Envelope.py` — hash `c5ee034c94439457`
- `dcs/verify_intoto.py` — hash `afa4f47d54e3fef9`

## `Sbom` — identical

- `governance/sbom/sbom.py` — hash `332270341e11d50e`
- `mark/sbom/sbom.py` — hash `332270341e11d50e`
- `sovereign-bounded-matrix/mark/sbom/sbom.py` — hash `332270341e11d50e`

## `Manifest` — all-different

- `app/core/manifest.py` — hash `646e93a2c3834be6`
- `app/seed/manifest.py` — hash `6ce7f8bea388a96d`
- `constructors/generated/Manifest.py` — hash `43bf19f3e31a49ee`

## `Witness` — all-different

- `app/canon/genesis.py` — hash `66b10907618f459e`
- `app/chain/witness.py` — hash `513f623b95bf71b2`
- `constructors/generated/Witness.py` — hash `38f6525d50c072d6`

## `Policy` — all-different

- `app/codeql/policy.py` — hash `6eaf525c49d12872`
- `app/policy/parser.py` — hash `8ae15d8ae0820076`
- `constructors/generated/Policy.py` — hash `63293b88ff7dfea8`

## `App` — identical

- `95_OPERATIONS/app/app.py` — hash `4fd6a3d327dc9371`
- `sovereign-bounded-matrix/platform/app/app.py` — hash `4fd6a3d327dc9371`
- `web/src/app/app.py` — hash `4fd6a3d327dc9371`

## `Api` — identical

- `aiops_platform/app/api/api.py` — hash `09a4ab05bc594f96`
- `sovereign-bounded-matrix/platform/app/api/api.py` — hash `09a4ab05bc594f96`
- `web/src/app/api/api.py` — hash `09a4ab05bc594f96`

## `Intent` — partial-overlap

- `app/seed/intent.py` — hash `662241ea35facf6d`
- `web/src/app/api/intent/intent.py` — hash `33f34e89d1497fb4`
- `web/src/app/intent/intent.py` — hash `33f34e89d1497fb4`

## `Run` — partial-overlap

- `app/meta/observer.py` — hash `37e981792898f0eb`
- `app/train/core.py` — hash `c0b8a6c74f90ad02`
- `tools/hooks/canonical_core.py` — hash `c0b8a6c74f90ad02`

## `Migrations` — identical

- `migrations/migrations.py` — hash `6270b294d88d68cf`
- `sovereign-bounded-matrix/platform/app/db/migrations/migrations.py` — hash `6270b294d88d68cf`

## `Symbol` — all-different

- `app/origami/grammar.py` — hash `ce2df1be39a5fb64`
- `tools/gen_grammar_spec.py` — hash `1970866e4f1dbcf9`

## `Mark` — identical

- `mark/mark.py` — hash `d663fba9ceeb8ccf`
- `sovereign-bounded-matrix/mark/mark.py` — hash `d663fba9ceeb8ccf`

## `Daemon` — identical

- `daemon/daemon.py` — hash `38837565431f0369`
- `sovereign-bounded-matrix/daemon/daemon.py` — hash `38837565431f0369`

## `Codeql` — identical

- `.github/codeql/codeql.py` — hash `292daccd77d8c9f9`
- `codeql/codeql.py` — hash `292daccd77d8c9f9`

## `Layer` — all-different

- `app/bridges/usd.py` — hash `59b3801bf6606e4e`
- `dcs/attest.py` — hash `adf8dc71a5aa4b2a`

## `Certification` — all-different

- `app/agency/primitives.py` — hash `d13783f35b9bdb78`
- `dcs/certify.py` — hash `9d5b2ea0fb1c7666`

## `Bundle` — all-different

- `constructors/generated/Bundle.py` — hash `7fdf3f6bee0eb151`
- `dcs/evidence.py` — hash `a2a546901036d3d5`

## `Core` — identical

- `dcs/core/core.py` — hash `d096aef7efb86f39`
- `sovereign-bounded-matrix/platform/app/core/core.py` — hash `d096aef7efb86f39`

## `Evidence` — all-different

- `constructors/generated/Evidence.py` — hash `2e884322342b0ede`
- `dcs/evidence/evidence.py` — hash `6dbb8554ae8d2a8d`

## `Receipt` — all-different

- `constructors/generated/Receipt.py` — hash `fdda34c8afff580c`
- `dcs/triad/kernel.py` — hash `926c4716495a57eb`

## `Metrics` — all-different

- `dcs/crosscut/observability.py` — hash `96a938e6f6d087da`
- `web/src/app/api/metrics/metrics.py` — hash `7289de0c53dba3fd`

## `License` — all-different

- `app/agency/primitives.py` — hash `68e15133a0f89a7e`
- `governance/license/license.py` — hash `5bb09f9c94bfeacc`

## `Audit` — identical

- `daemon/audit/audit.py` — hash `281ccd2b3bf78e15`
- `sovereign-bounded-matrix/daemon/audit/audit.py` — hash `281ccd2b3bf78e15`

## `Supervisor` — identical

- `daemon/supervisor/supervisor.py` — hash `5d834bb4f77405ce`
- `sovereign-bounded-matrix/daemon/supervisor/supervisor.py` — hash `5d834bb4f77405ce`

## `Spec` — all-different

- `app/seed/spec.py` — hash `3c1fbe4971b7329c`
- `ncf_layer/spec/spec.py` — hash `1b0f4c878654127d`

## `Event` — all-different

- `app/core/ram_substrate.py` — hash `6186876c91b0f656`
- `constructors/generated/Event.py` — hash `fcdf51fc0cf1cad6`

## `Signal` — all-different

- `app/murmur/state.py` — hash `dbd04d6d96a0d048`
- `constructors/generated/Signal.py` — hash `1b7b621654ed6867`

## `Outcome` — all-different

- `app/engines/parallel.py` — hash `5760d94e6648d8ef`
- `constructors/generated/Outcome.py` — hash `797cb21b34c51058`

## `Capability` — all-different

- `app/cst/predicate.py` — hash `46712394a5f8d90b`
- `constructors/generated/Capability.py` — hash `6244a3f042899ba5`

## `PolicyError` — all-different

- `app/core/state_machine.py` — hash `b601788c32a001c4`
- `constructors/generated/PolicyError.py` — hash `a8c9b373b96a95b6`

## `Proof` — all-different

- `constructors/generated/Proof.py` — hash `017fc29bb2f400e4`
- `vatican/proof/proof.py` — hash `bebe7589f8dfb633`

## `EvidenceRecord` — all-different

- `app/dispatch/evidence/base.py` — hash `d3f3505ec0c7d472`
- `constructors/generated/EvidenceRecord.py` — hash `65fc7c21d536d1b4`

## `Certificates` — identical

- `mark/certificates/certificates.py` — hash `23ec718f3adb07b8`
- `sovereign-bounded-matrix/mark/certificates/certificates.py` — hash `23ec718f3adb07b8`

## `Db` — identical

- `aiops_platform/app/db/db.py` — hash `7b00479ea89b0fc7`
- `sovereign-bounded-matrix/platform/app/db/db.py` — hash `7b00479ea89b0fc7`

## `Grid` — all-different

- `04_INTERFACING/grid/grid.py` — hash `38c800841a357f67`
- `app/puzzles/grid.py` — hash `e2d988d538731ad9`

## `TrainConfig` — identical

- `app/train/core.py` — hash `cf60cb078bda81e6`
- `tools/hooks/canonical_core.py` — hash `cf60cb078bda81e6`

## `TrainOutcome` — identical

- `app/train/core.py` — hash `aaf0df58f7565c4d`
- `tools/hooks/canonical_core.py` — hash `aaf0df58f7565c4d`

## `TrainTile` — identical

- `app/train/core.py` — hash `1acf26a991202a0d`
- `tools/hooks/canonical_core.py` — hash `1acf26a991202a0d`

## `Trainer` — identical

- `app/train/core.py` — hash `0f779a626341e621`
- `tools/hooks/canonical_core.py` — hash `0f779a626341e621`

## `MeshOfMeshes` — identical

- `app/train/mesh.py` — hash `5316676d71a6d952`
- `tools/hooks/canonical_mesh.py` — hash `5316676d71a6d952`
