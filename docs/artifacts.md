# Layer: artifacts

Directory: `artifacts`

## Files

    artifacts/alerts/alerts.yaml
    artifacts/capabilities/cap.example.yaml
    artifacts/catalogs/nature.txt
    artifacts/certs/.gitkeep
    artifacts/ci/ci.yml
    artifacts/code/lib.py
    artifacts/code/main.py
    artifacts/config/config.json
    artifacts/config/config.yaml
    artifacts/contracts/service.contract.yaml
    artifacts/dashboards/overview.json
    artifacts/data/sample.csv
    artifacts/data/sample.json
    artifacts/deploy/deploy.yaml
    artifacts/docs/decisions/0001-example.md
    artifacts/docs/reference/.gitkeep
    artifacts/docs/runbooks/incident.md
    artifacts/docs/tutorials/getting-started.md
    artifacts/evidence/attestation.json
    artifacts/evidence/soc2.md
    artifacts/flags/flags.yaml
    artifacts/handoff/HANDOFF.md
    artifacts/INDEX.md
    artifacts/interfaces/service.proto
    artifacts/journals/journal.jsonl
    artifacts/keys/README.md
    artifacts/ledgers/ledger.jsonl
    artifacts/licenses/LICENSE
    artifacts/licenses/THIRD_PARTY.md
    artifacts/lockfiles/lock.json
    artifacts/logs/log.schema.json
    artifacts/manifests/manifest.yaml
    artifacts/metrics/metrics.yaml
    artifacts/models/MODELCARD.md
    artifacts/notebooks/explore.ipynb
    artifacts/oncall/oncall.yaml
    artifacts/operators/operators.yaml
    artifacts/permissions/roles.yaml
    artifacts/policies/policy.rego
    artifacts/predicates/predicates.py
    artifacts/profiles/dev.yaml
    artifacts/profiles/prod.yaml
    artifacts/prompts/capability.translate.txt
    artifacts/prompts/system.txt
    artifacts/provenance/slsa.json
    artifacts/registries/code/.gitkeep
    artifacts/registries/evidence/.gitkeep
    artifacts/registries/gates/.gitkeep
    artifacts/registries/manifold/.gitkeep
    artifacts/registries/operators/.gitkeep
    artifacts/registries/provenance/.gitkeep
    artifacts/registries/specs/.gitkeep
    artifacts/registries/types/.gitkeep
    artifacts/release/release-notes.md
    artifacts/sbom/cyclonedx.json
    artifacts/schemas/example.schema.yaml
    artifacts/scripts/run.sh
    artifacts/secrets/.env.example
    artifacts/specs/SPEC-0001.md
    artifacts/taxonomies/capabilities.json
    artifacts/taxonomies/components.json
    artifacts/templates/service.py.j2
    artifacts/tests/fixtures/conftest.py
    artifacts/tests/fuzz/.gitkeep
    artifacts/tests/integration/.gitkeep
    artifacts/tests/property/.gitkeep
    artifacts/tests/unit/test_smoke.py
    artifacts/traces/.gitkeep
    artifacts/types/types.py
    artifacts/types/types.ts

## Contents

### `artifacts/alerts/alerts.yaml`

```
groups: []
```
### `artifacts/capabilities/cap.example.yaml`

```
id: cap.example.001.example
inputs: []
limits: {max_concurrency: 1, max_seconds: 60}
permissions: []
evidence_required: [test]
implementation: {status: declared}
```
### `artifacts/catalogs/nature.txt`

```
# code | description
```
### `artifacts/certs/.gitkeep`

```
```
### `artifacts/ci/ci.yml`

```
name: ci
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
```
### `artifacts/code/lib.py`

```
"""Library module."""
```
### `artifacts/code/main.py`

```
#!/usr/bin/env python3
"""Entry point."""


def main() -> int:
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
### `artifacts/config/config.json`

```
{
  "version": 1
}
```
### `artifacts/config/config.yaml`

```
version: 1
```
### `artifacts/contracts/service.contract.yaml`

```
id: contract://example@1.0.0
pre: []
post: []
invariants: []
```
### `artifacts/dashboards/overview.json`

```
{
  "title": "Overview",
  "panels": []
}
```
### `artifacts/data/sample.csv`

```
id,value
1,example
```
### `artifacts/data/sample.json`

```
{
  "items": []
}
```
### `artifacts/deploy/deploy.yaml`

```
kind: Deployment
metadata: {name: example}
```
### `artifacts/docs/decisions/0001-example.md`

```
# ADR 0001: Example Decision

- Status: proposed
- Context:
- Decision:
- Consequences:
```
### `artifacts/docs/reference/.gitkeep`

```
```
### `artifacts/docs/runbooks/incident.md`

```
# Incident Runbook

1. Detect
2. Triage
3. Mitigate
4. Postmortem
```
### `artifacts/docs/tutorials/getting-started.md`

```
# Getting Started
```
### `artifacts/evidence/attestation.json`

```
{
  "kind": "attestation",
  "signer": "ci",
  "result": "pass"
}
```
### `artifacts/evidence/soc2.md`

```
# SOC 2 Evidence

- Control:
- Evidence:
- Reviewer:
```
### `artifacts/flags/flags.yaml`

```
features: {}
```
### `artifacts/handoff/HANDOFF.md`

```
# Handoff

- From:
- To:
- State:
- Open items:
```
### `artifacts/INDEX.md`

```
# Artifact Sets

Total sets: 60

- [`artifacts/code`](./code) — `code` — Executable implementation in any language.
- [`artifacts/scripts`](./scripts) — `script` — Operational / one-off scripts.
- [`artifacts/notebooks`](./notebooks) — `notebook` — Exploratory and analysis notebooks.
- [`artifacts/types`](./types) — `types` — Type definitions, constructors, refinements.
- [`artifacts/interfaces`](./interfaces) — `interface` — Formal interface declarations.
- [`artifacts/operators`](./operators) — `operator` — AST operators and grammar extensions.
- [`artifacts/specs`](./specs) — `spec` — Requirements and behavioural specs.
- [`artifacts/contracts`](./contracts) — `contract` — Pre/postconditions and invariants.
- [`artifacts/predicates`](./predicates) — `predicate` — Checkable logical predicates.
- [`artifacts/schemas`](./schemas) — `schema` — Data and config schemas.
- [`artifacts/data`](./data) — `data` — Datasets, fixtures, seed data.
- [`artifacts/models`](./models) — `model` — Model manifests and cards.
- [`artifacts/config`](./config) — `config` — Runtime and build configuration.
- [`artifacts/flags`](./flags) — `flag` — Feature flags.
- [`artifacts/profiles`](./profiles) — `profile` — Configuration profiles.
- [`artifacts/policies`](./policies) — `policy` — Policy definitions (OPA/Rego or YAML).
- [`artifacts/permissions`](./permissions) — `permission` — Permission and role definitions.
- [`artifacts/capabilities`](./capabilities) — `capability` — Capability contracts.
- [`artifacts/registries/code`](./registries/code) — `registry` — Code registry entries.
- [`artifacts/registries/types`](./registries/types) — `registry` — Type registry entries.
- [`artifacts/registries/operators`](./registries/operators) — `registry` — Operator registry entries.
- [`artifacts/registries/specs`](./registries/specs) — `registry` — Spec registry entries.
- [`artifacts/registries/gates`](./registries/gates) — `registry` — Gate registry entries.
- [`artifacts/registries/evidence`](./registries/evidence) — `registry` — Evidence registry entries.
- [`artifacts/registries/manifold`](./registries/manifold) — `registry` — Manifold registry entries.
- [`artifacts/registries/provenance`](./registries/provenance) — `registry` — Provenance registry entries.
- [`artifacts/manifests`](./manifests) — `manifest` — Library manifests tying the seven faces.
- [`artifacts/lockfiles`](./lockfiles) — `lockfile` — Locked dependency graphs.
- [`artifacts/prompts`](./prompts) — `prompt` — Prompt templates for models and agents.
- [`artifacts/templates`](./templates) — `template` — Scaffolding and code-gen templates.
- [`artifacts/evidence`](./evidence) — `evidence` — Compliance and verification evidence.
- [`artifacts/provenance`](./provenance) — `provenance` — Chain-of-custody records.
- [`artifacts/sbom`](./sbom) — `sbom` — Software bills of materials.
- [`artifacts/licenses`](./licenses) — `license` — License and notice files.
- [`artifacts/tests/unit`](./tests/unit) — `test` — Unit tests.
- [`artifacts/tests/integration`](./tests/integration) — `test` — Integration tests.
- [`artifacts/tests/property`](./tests/property) — `test` — Property-based tests.
- [`artifacts/tests/fuzz`](./tests/fuzz) — `test` — Fuzz targets.
- [`artifacts/tests/fixtures`](./tests/fixtures) — `fixture` — Shared test fixtures.
- [`artifacts/metrics`](./metrics) — `metric` — Metric definitions.
- [`artifacts/logs`](./logs) — `log` — Log schema definitions.
- [`artifacts/traces`](./traces) — `trace` — Trace schema and spans.
- [`artifacts/alerts`](./alerts) — `alert` — Alert rules.
- [`artifacts/dashboards`](./dashboards) — `dashboard` — Dashboard definitions.
- [`artifacts/ci`](./ci) — `ci` — Continuous integration workflows.
- [`artifacts/release`](./release) — `release` — Release workflows and notes.
- [`artifacts/deploy`](./deploy) — `deploy` — Deployment definitions.
- [`artifacts/docs/reference`](./docs/reference) — `doc` — Reference docs.
- [`artifacts/docs/tutorials`](./docs/tutorials) — `doc` — Tutorials.
- [`artifacts/docs/runbooks`](./docs/runbooks) — `doc` — Operational runbooks.
- [`artifacts/docs/decisions`](./docs/decisions) — `adr` — Architecture decision records.
- [`artifacts/taxonomies`](./taxonomies) — `taxonomy` — Component and capability taxonomies.
- [`artifacts/catalogs`](./catalogs) — `catalog` — Flat catalogs of known things.
- [`artifacts/ledgers`](./ledgers) — `ledger` — Append-only ledgers.
- [`artifacts/journals`](./journals) — `journal` — Decision and change journals.
- [`artifacts/handoff`](./handoff) — `handoff` — Handoff notes between owners.
- [`artifacts/oncall`](./oncall) — `oncall` — On-call rotations and escalation.
- [`artifacts/keys`](./keys) — `key` — Public keys and key metadata.
- [`artifacts/certs`](./certs) — `cert` — Certificates.
- [`artifacts/secrets`](./secrets) — `secret` — Secret templates (never real secrets).
```
### `artifacts/interfaces/service.proto`

```
syntax = "proto3";

package aether;

message Request { string id = 1; }
message Response { string id = 1; bool ok = 2; }
service Greeter { rpc Hello (Request) returns (Response); }
```
### `artifacts/journals/journal.jsonl`

```
```
### `artifacts/keys/README.md`

```
# Keys

Private keys are never stored in the repo.
```
### `artifacts/ledgers/ledger.jsonl`

```
```
### `artifacts/licenses/LICENSE`

```
SPDX-License-Identifier: Apache-2.0
```
### `artifacts/licenses/THIRD_PARTY.md`

```
# Third-Party Notices
```
### `artifacts/lockfiles/lock.json`

```
{
  "version": 1,
  "resolved": []
}
```
### `artifacts/logs/log.schema.json`

```
{
  "level": "string",
  "ts": "string",
  "msg": "string"
}
```
### `artifacts/manifests/manifest.yaml`

```
library: example/example
version: 0.0.1
entries:
  code: code://example/example@0.0.1
  types: types://example/example@0.0.1
  operators: operators://example/example@0.0.1
  specs: specs://example/example@0.0.1
  gates: gates://example/example@0.0.1
  evidence: evidence://example/example@0.0.1
  provenance: provenance://example/example@0.0.1
```
### `artifacts/metrics/metrics.yaml`

```
metrics:
  - name: request_total
    type: counter
    help: Total requests
```
### `artifacts/models/MODELCARD.md`

```
# Model Card

- Name:
- Version:
- Intended use:
```
### `artifacts/notebooks/explore.ipynb`

```
{
  "cells": [],
  "metadata": {},
  "nbformat": 4,
  "nbformat_minor": 5
}
```
### `artifacts/oncall/oncall.yaml`

```
rotation: []
escalation: []
```
### `artifacts/operators/operators.yaml`

```
id: operators://core@1.0.0
kind: operators
operators: []
```
### `artifacts/permissions/roles.yaml`

```
roles:
  - name: reader
    permissions: [read]
  - name: writer
    permissions: [read, write]
```
### `artifacts/policies/policy.rego`

```
package aether

default allow = false

allow { input.kind == "allowed" }
```
### `artifacts/predicates/predicates.py`

```
"""Predicates used by gates."""


def is_non_empty(value) -> bool:
    return bool(value)
```
### `artifacts/profiles/dev.yaml`

```
profile: dev
```
### `artifacts/profiles/prod.yaml`

```
profile: prod
```
### `artifacts/prompts/capability.translate.txt`

```
Translate the following into {target_language}:

{input}
```
### `artifacts/prompts/system.txt`

```
You are a helpful assistant.
```
### `artifacts/provenance/slsa.json`

```
{
  "slsa": 3,
  "reproducibility": "hermetic"
}
```
### `artifacts/registries/code/.gitkeep`

```
```
### `artifacts/registries/evidence/.gitkeep`

```
```
### `artifacts/registries/gates/.gitkeep`

```
```
### `artifacts/registries/manifold/.gitkeep`

```
```
### `artifacts/registries/operators/.gitkeep`

```
```
### `artifacts/registries/provenance/.gitkeep`

```
```
### `artifacts/registries/specs/.gitkeep`

```
```
### `artifacts/registries/types/.gitkeep`

```
```
### `artifacts/release/release-notes.md`

```
# Release Notes
```
### `artifacts/sbom/cyclonedx.json`

```
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "components": []
}
```
### `artifacts/schemas/example.schema.yaml`

```
$schema: "https://json-schema.org/draft/2020-12/schema"
title: Example
type: object
properties:
  id: {type: string}
```
### `artifacts/scripts/run.sh`

```
#!/usr/bin/env bash
set -euo pipefail
echo ok
```
### `artifacts/secrets/.env.example`

```
API_KEY=
DATABASE_URL=
```
### `artifacts/specs/SPEC-0001.md`

```
# SPEC-0001 — Example

## Requirements

- R-001: When X, the system shall Y.
```
### `artifacts/taxonomies/capabilities.json`

```
{
  "schema": "aether.capabilities.v1",
  "capabilities": []
}
```
### `artifacts/taxonomies/components.json`

```
{
  "schema": "aether.components.v1",
  "families": []
}
```
### `artifacts/templates/service.py.j2`

```
class {{ name }}:
    pass
```
### `artifacts/tests/fixtures/conftest.py`

```
"""Shared fixtures."""
```
### `artifacts/tests/fuzz/.gitkeep`

```
```
### `artifacts/tests/integration/.gitkeep`

```
```
### `artifacts/tests/property/.gitkeep`

```
```
### `artifacts/tests/unit/test_smoke.py`

```
def test_smoke():
    assert True
```
### `artifacts/traces/.gitkeep`

```
```
### `artifacts/types/types.py`

```
from __future__ import annotations

from typing import Protocol


class Service(Protocol):
    def handle(self, payload: dict) -> dict: ...
```
### `artifacts/types/types.ts`

```
export interface Service {
  handle(payload: Record<string, unknown>): Record<string, unknown>;
}
```
