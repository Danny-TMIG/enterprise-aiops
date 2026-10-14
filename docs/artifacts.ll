;; layer: artifacts
;; dir:   artifacts
FILE artifacts/alerts/alerts.yaml
groups: []
ENDFILE artifacts/alerts/alerts.yaml
FILE artifacts/capabilities/cap.example.yaml
id: cap.example.001.example
inputs: []
limits: {max_concurrency: 1, max_seconds: 60}
permissions: []
evidence_required: [test]
implementation: {status: declared}
ENDFILE artifacts/capabilities/cap.example.yaml
FILE artifacts/catalogs/nature.txt
# code | description
ENDFILE artifacts/catalogs/nature.txt
FILE artifacts/certs/.gitkeep
ENDFILE artifacts/certs/.gitkeep
FILE artifacts/ci/ci.yml
name: ci
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
ENDFILE artifacts/ci/ci.yml
FILE artifacts/code/lib.py
"""Library module."""
ENDFILE artifacts/code/lib.py
FILE artifacts/code/main.py
#!/usr/bin/env python3
"""Entry point."""


def main() -> int:
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
ENDFILE artifacts/code/main.py
FILE artifacts/config/config.json
{
  "version": 1
}
ENDFILE artifacts/config/config.json
FILE artifacts/config/config.yaml
version: 1
ENDFILE artifacts/config/config.yaml
FILE artifacts/contracts/service.contract.yaml
id: contract://example@1.0.0
pre: []
post: []
invariants: []
ENDFILE artifacts/contracts/service.contract.yaml
FILE artifacts/dashboards/overview.json
{
  "title": "Overview",
  "panels": []
}
ENDFILE artifacts/dashboards/overview.json
FILE artifacts/data/sample.csv
id,value
1,example
ENDFILE artifacts/data/sample.csv
FILE artifacts/data/sample.json
{
  "items": []
}
ENDFILE artifacts/data/sample.json
FILE artifacts/deploy/deploy.yaml
kind: Deployment
metadata: {name: example}
ENDFILE artifacts/deploy/deploy.yaml
FILE artifacts/docs/decisions/0001-example.md
# ADR 0001: Example Decision

- Status: proposed
- Context:
- Decision:
- Consequences:
ENDFILE artifacts/docs/decisions/0001-example.md
FILE artifacts/docs/reference/.gitkeep
ENDFILE artifacts/docs/reference/.gitkeep
FILE artifacts/docs/runbooks/incident.md
# Incident Runbook

1. Detect
2. Triage
3. Mitigate
4. Postmortem
ENDFILE artifacts/docs/runbooks/incident.md
FILE artifacts/docs/tutorials/getting-started.md
# Getting Started
ENDFILE artifacts/docs/tutorials/getting-started.md
FILE artifacts/evidence/attestation.json
{
  "kind": "attestation",
  "signer": "ci",
  "result": "pass"
}
ENDFILE artifacts/evidence/attestation.json
FILE artifacts/evidence/soc2.md
# SOC 2 Evidence

- Control:
- Evidence:
- Reviewer:
ENDFILE artifacts/evidence/soc2.md
FILE artifacts/flags/flags.yaml
features: {}
ENDFILE artifacts/flags/flags.yaml
FILE artifacts/handoff/HANDOFF.md
# Handoff

- From:
- To:
- State:
- Open items:
ENDFILE artifacts/handoff/HANDOFF.md
FILE artifacts/INDEX.md
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
ENDFILE artifacts/INDEX.md
FILE artifacts/interfaces/service.proto
syntax = "proto3";

package aether;

message Request { string id = 1; }
message Response { string id = 1; bool ok = 2; }
service Greeter { rpc Hello (Request) returns (Response); }
ENDFILE artifacts/interfaces/service.proto
FILE artifacts/journals/journal.jsonl
ENDFILE artifacts/journals/journal.jsonl
FILE artifacts/keys/README.md
# Keys

Private keys are never stored in the repo.
ENDFILE artifacts/keys/README.md
FILE artifacts/ledgers/ledger.jsonl
ENDFILE artifacts/ledgers/ledger.jsonl
FILE artifacts/licenses/LICENSE
SPDX-License-Identifier: Apache-2.0
ENDFILE artifacts/licenses/LICENSE
FILE artifacts/licenses/THIRD_PARTY.md
# Third-Party Notices
ENDFILE artifacts/licenses/THIRD_PARTY.md
FILE artifacts/lockfiles/lock.json
{
  "version": 1,
  "resolved": []
}
ENDFILE artifacts/lockfiles/lock.json
FILE artifacts/logs/log.schema.json
{
  "level": "string",
  "ts": "string",
  "msg": "string"
}
ENDFILE artifacts/logs/log.schema.json
FILE artifacts/manifests/manifest.yaml
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
ENDFILE artifacts/manifests/manifest.yaml
FILE artifacts/metrics/metrics.yaml
metrics:
  - name: request_total
    type: counter
    help: Total requests
ENDFILE artifacts/metrics/metrics.yaml
FILE artifacts/models/MODELCARD.md
# Model Card

- Name:
- Version:
- Intended use:
ENDFILE artifacts/models/MODELCARD.md
FILE artifacts/notebooks/explore.ipynb
{
  "cells": [],
  "metadata": {},
  "nbformat": 4,
  "nbformat_minor": 5
}
ENDFILE artifacts/notebooks/explore.ipynb
FILE artifacts/oncall/oncall.yaml
rotation: []
escalation: []
ENDFILE artifacts/oncall/oncall.yaml
FILE artifacts/operators/operators.yaml
id: operators://core@1.0.0
kind: operators
operators: []
ENDFILE artifacts/operators/operators.yaml
FILE artifacts/permissions/roles.yaml
roles:
  - name: reader
    permissions: [read]
  - name: writer
    permissions: [read, write]
ENDFILE artifacts/permissions/roles.yaml
FILE artifacts/policies/policy.rego
package aether

default allow = false

allow { input.kind == "allowed" }
ENDFILE artifacts/policies/policy.rego
FILE artifacts/predicates/predicates.py
"""Predicates used by gates."""


def is_non_empty(value) -> bool:
    return bool(value)
ENDFILE artifacts/predicates/predicates.py
FILE artifacts/profiles/dev.yaml
profile: dev
ENDFILE artifacts/profiles/dev.yaml
FILE artifacts/profiles/prod.yaml
profile: prod
ENDFILE artifacts/profiles/prod.yaml
FILE artifacts/prompts/capability.translate.txt
Translate the following into {target_language}:

{input}
ENDFILE artifacts/prompts/capability.translate.txt
FILE artifacts/prompts/system.txt
You are a helpful assistant.
ENDFILE artifacts/prompts/system.txt
FILE artifacts/provenance/slsa.json
{
  "slsa": 3,
  "reproducibility": "hermetic"
}
ENDFILE artifacts/provenance/slsa.json
FILE artifacts/registries/code/.gitkeep
ENDFILE artifacts/registries/code/.gitkeep
FILE artifacts/registries/evidence/.gitkeep
ENDFILE artifacts/registries/evidence/.gitkeep
FILE artifacts/registries/gates/.gitkeep
ENDFILE artifacts/registries/gates/.gitkeep
FILE artifacts/registries/manifold/.gitkeep
ENDFILE artifacts/registries/manifold/.gitkeep
FILE artifacts/registries/operators/.gitkeep
ENDFILE artifacts/registries/operators/.gitkeep
FILE artifacts/registries/provenance/.gitkeep
ENDFILE artifacts/registries/provenance/.gitkeep
FILE artifacts/registries/specs/.gitkeep
ENDFILE artifacts/registries/specs/.gitkeep
FILE artifacts/registries/types/.gitkeep
ENDFILE artifacts/registries/types/.gitkeep
FILE artifacts/release/release-notes.md
# Release Notes
ENDFILE artifacts/release/release-notes.md
FILE artifacts/sbom/cyclonedx.json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "components": []
}
ENDFILE artifacts/sbom/cyclonedx.json
FILE artifacts/schemas/example.schema.yaml
$schema: "https://json-schema.org/draft/2020-12/schema"
title: Example
type: object
properties:
  id: {type: string}
ENDFILE artifacts/schemas/example.schema.yaml
FILE artifacts/scripts/run.sh
#!/usr/bin/env bash
set -euo pipefail
echo ok
ENDFILE artifacts/scripts/run.sh
FILE artifacts/secrets/.env.example
API_KEY=
DATABASE_URL=
ENDFILE artifacts/secrets/.env.example
FILE artifacts/specs/SPEC-0001.md
# SPEC-0001 — Example

## Requirements

- R-001: When X, the system shall Y.
ENDFILE artifacts/specs/SPEC-0001.md
FILE artifacts/taxonomies/capabilities.json
{
  "schema": "aether.capabilities.v1",
  "capabilities": []
}
ENDFILE artifacts/taxonomies/capabilities.json
FILE artifacts/taxonomies/components.json
{
  "schema": "aether.components.v1",
  "families": []
}
ENDFILE artifacts/taxonomies/components.json
FILE artifacts/templates/service.py.j2
class {{ name }}:
    pass
ENDFILE artifacts/templates/service.py.j2
FILE artifacts/tests/fixtures/conftest.py
"""Shared fixtures."""
ENDFILE artifacts/tests/fixtures/conftest.py
FILE artifacts/tests/fuzz/.gitkeep
ENDFILE artifacts/tests/fuzz/.gitkeep
FILE artifacts/tests/integration/.gitkeep
ENDFILE artifacts/tests/integration/.gitkeep
FILE artifacts/tests/property/.gitkeep
ENDFILE artifacts/tests/property/.gitkeep
FILE artifacts/tests/unit/test_smoke.py
def test_smoke():
    assert True
ENDFILE artifacts/tests/unit/test_smoke.py
FILE artifacts/traces/.gitkeep
ENDFILE artifacts/traces/.gitkeep
FILE artifacts/types/types.py
from __future__ import annotations

from typing import Protocol


class Service(Protocol):
    def handle(self, payload: dict) -> dict: ...
ENDFILE artifacts/types/types.py
FILE artifacts/types/types.ts
export interface Service {
  handle(payload: Record<string, unknown>): Record<string, unknown>;
}
ENDFILE artifacts/types/types.ts
