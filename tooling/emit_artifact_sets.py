#!/usr/bin/env python3
"""Materialize every known artifact set as directories + stubs.

Each "artifact set" is a named family of files that a system of this kind
needs. We enumerate the sets, create their directories, and write a
CANONICAL.md in each one describing what belongs there. Stub artifacts
(the smallest valid file of each kind) are written next to it.

Idempotent: existing files are left alone unless --force is passed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORCE = "--force" in sys.argv

# ---------------------------------------------------------------------------
# The artifact sets. Each entry is (dir, kind, description, [stub_files]).
# ---------------------------------------------------------------------------
ARTIFACT_SETS: list[tuple[str, str, str, list[tuple[str, str]]]] = [
    # --- source code & implementation ---
    ("artifacts/code", "code", "Executable implementation in any language.", [
        ("main.py", "#!/usr/bin/env python3\n\"\"\"Entry point.\"\"\"\n\n\ndef main() -> int:\n    return 0\n\n\nif __name__ == \"__main__\":\n    raise SystemExit(main())\n"),
        ("lib.py", "\"\"\"Library module.\"\"\"\n"),
    ]),
    ("artifacts/scripts", "script", "Operational / one-off scripts.", [
        ("run.sh", "#!/usr/bin/env bash\nset -euo pipefail\necho ok\n"),
    ]),
    ("artifacts/notebooks", "notebook", "Exploratory and analysis notebooks.", [
        ("explore.ipynb", json.dumps({"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}, indent=2) + "\n"),
    ]),

    # --- type & interface definitions ---
    ("artifacts/types", "types", "Type definitions, constructors, refinements.", [
        ("types.py", "from __future__ import annotations\n\nfrom typing import Protocol\n\n\nclass Service(Protocol):\n    def handle(self, payload: dict) -> dict: ...\n"),
        ("types.ts", "export interface Service {\n  handle(payload: Record<string, unknown>): Record<string, unknown>;\n}\n"),
    ]),
    ("artifacts/interfaces", "interface", "Formal interface declarations.", [
        ("service.proto", "syntax = \"proto3\";\n\npackage aether;\n\nmessage Request { string id = 1; }\nmessage Response { string id = 1; bool ok = 2; }\nservice Greeter { rpc Hello (Request) returns (Response); }\n"),
    ]),
    ("artifacts/operators", "operator", "AST operators and grammar extensions.", [
        ("operators.yaml", "id: operators://core@1.0.0\nkind: operators\noperators: []\n"),
    ]),

    # --- specs & contracts ---
    ("artifacts/specs", "spec", "Requirements and behavioural specs.", [
        ("SPEC-0001.md", "# SPEC-0001 — Example\n\n## Requirements\n\n- R-001: When X, the system shall Y.\n"),
    ]),
    ("artifacts/contracts", "contract", "Pre/postconditions and invariants.", [
        ("service.contract.yaml", "id: contract://example@1.0.0\npre: []\npost: []\ninvariants: []\n"),
    ]),
    ("artifacts/predicates", "predicate", "Checkable logical predicates.", [
        ("predicates.py", "\"\"\"Predicates used by gates.\"\"\"\n\n\ndef is_non_empty(value) -> bool:\n    return bool(value)\n"),
    ]),

    # --- schemas & data ---
    ("artifacts/schemas", "schema", "Data and config schemas.", [
        ("example.schema.yaml", "$schema: \"https://json-schema.org/draft/2020-12/schema\"\ntitle: Example\ntype: object\nproperties:\n  id: {type: string}\n"),
    ]),
    ("artifacts/data", "data", "Datasets, fixtures, seed data.", [
        ("sample.json", "{\n  \"items\": []\n}\n"),
        ("sample.csv", "id,value\n1,example\n"),
    ]),
    ("artifacts/models", "model", "Model manifests and cards.", [
        ("MODELCARD.md", "# Model Card\n\n- Name:\n- Version:\n- Intended use:\n"),
    ]),

    # --- configuration ---
    ("artifacts/config", "config", "Runtime and build configuration.", [
        ("config.yaml", "version: 1\n"),
        ("config.json", "{\n  \"version\": 1\n}\n"),
    ]),
    ("artifacts/flags", "flag", "Feature flags.", [
        ("flags.yaml", "features: {}\n"),
    ]),
    ("artifacts/profiles", "profile", "Configuration profiles.", [
        ("dev.yaml", "profile: dev\n"),
        ("prod.yaml", "profile: prod\n"),
    ]),

    # --- policies & governance ---
    ("artifacts/policies", "policy", "Policy definitions (OPA/Rego or YAML).", [
        ("policy.rego", "package aether\n\ndefault allow = false\n\nallow { input.kind == \"allowed\" }\n"),
    ]),
    ("artifacts/permissions", "permission", "Permission and role definitions.", [
        ("roles.yaml", "roles:\n  - name: reader\n    permissions: [read]\n  - name: writer\n    permissions: [read, write]\n"),
    ]),
    ("artifacts/capabilities", "capability", "Capability contracts.", [
        ("cap.example.yaml", "id: cap.example.001.example\ninputs: []\nlimits: {max_concurrency: 1, max_seconds: 60}\npermissions: []\nevidence_required: [test]\nimplementation: {status: declared}\n"),
    ]),

    # --- registries ---
    ("artifacts/registries/code", "registry", "Code registry entries.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/registries/types", "registry", "Type registry entries.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/registries/operators", "registry", "Operator registry entries.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/registries/specs", "registry", "Spec registry entries.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/registries/gates", "registry", "Gate registry entries.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/registries/evidence", "registry", "Evidence registry entries.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/registries/manifold", "registry", "Manifold registry entries.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/registries/provenance", "registry", "Provenance registry entries.", [
        (".gitkeep", ""),
    ]),

    # --- manifests & lockfiles ---
    ("artifacts/manifests", "manifest", "Library manifests tying the seven faces.", [
        ("manifest.yaml", "library: example/example\nversion: 0.0.1\nentries:\n  code: code://example/example@0.0.1\n  types: types://example/example@0.0.1\n  operators: operators://example/example@0.0.1\n  specs: specs://example/example@0.0.1\n  gates: gates://example/example@0.0.1\n  evidence: evidence://example/example@0.0.1\n  provenance: provenance://example/example@0.0.1\n"),
    ]),
    ("artifacts/lockfiles", "lockfile", "Locked dependency graphs.", [
        ("lock.json", "{\n  \"version\": 1,\n  \"resolved\": []\n}\n"),
    ]),

    # --- prompts & templates ---
    ("artifacts/prompts", "prompt", "Prompt templates for models and agents.", [
        ("system.txt", "You are a helpful assistant.\n"),
        ("capability.translate.txt", "Translate the following into {target_language}:\n\n{input}\n"),
    ]),
    ("artifacts/templates", "template", "Scaffolding and code-gen templates.", [
        ("service.py.j2", "class {{ name }}:\n    pass\n"),
    ]),

    # --- evidence & provenance ---
    ("artifacts/evidence", "evidence", "Compliance and verification evidence.", [
        ("attestation.json", "{\n  \"kind\": \"attestation\",\n  \"signer\": \"ci\",\n  \"result\": \"pass\"\n}\n"),
        ("soc2.md", "# SOC 2 Evidence\n\n- Control:\n- Evidence:\n- Reviewer:\n"),
    ]),
    ("artifacts/provenance", "provenance", "Chain-of-custody records.", [
        ("slsa.json", "{\n  \"slsa\": 3,\n  \"reproducibility\": \"hermetic\"\n}\n"),
    ]),
    ("artifacts/sbom", "sbom", "Software bills of materials.", [
        ("cyclonedx.json", "{\n  \"bomFormat\": \"CycloneDX\",\n  \"specVersion\": \"1.5\",\n  \"components\": []\n}\n"),
    ]),
    ("artifacts/licenses", "license", "License and notice files.", [
        ("LICENSE", "SPDX-License-Identifier: Apache-2.0\n"),
        ("THIRD_PARTY.md", "# Third-Party Notices\n"),
    ]),

    # --- tests ---
    ("artifacts/tests/unit", "test", "Unit tests.", [
        ("test_smoke.py", "def test_smoke():\n    assert True\n"),
    ]),
    ("artifacts/tests/integration", "test", "Integration tests.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/tests/property", "test", "Property-based tests.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/tests/fuzz", "test", "Fuzz targets.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/tests/fixtures", "fixture", "Shared test fixtures.", [
        ("conftest.py", "\"\"\"Shared fixtures.\"\"\"\n"),
    ]),

    # --- observability ---
    ("artifacts/metrics", "metric", "Metric definitions.", [
        ("metrics.yaml", "metrics:\n  - name: request_total\n    type: counter\n    help: Total requests\n"),
    ]),
    ("artifacts/logs", "log", "Log schema definitions.", [
        ("log.schema.json", "{\n  \"level\": \"string\",\n  \"ts\": \"string\",\n  \"msg\": \"string\"\n}\n"),
    ]),
    ("artifacts/traces", "trace", "Trace schema and spans.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/alerts", "alert", "Alert rules.", [
        ("alerts.yaml", "groups: []\n"),
    ]),
    ("artifacts/dashboards", "dashboard", "Dashboard definitions.", [
        ("overview.json", "{\n  \"title\": \"Overview\",\n  \"panels\": []\n}\n"),
    ]),

    # --- CI / CD ---
    ("artifacts/ci", "ci", "Continuous integration workflows.", [
        ("ci.yml", "name: ci\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n"),
    ]),
    ("artifacts/release", "release", "Release workflows and notes.", [
        ("release-notes.md", "# Release Notes\n"),
    ]),
    ("artifacts/deploy", "deploy", "Deployment definitions.", [
        ("deploy.yaml", "kind: Deployment\nmetadata: {name: example}\n"),
    ]),

    # --- docs ---
    ("artifacts/docs/reference", "doc", "Reference docs.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/docs/tutorials", "doc", "Tutorials.", [
        ("getting-started.md", "# Getting Started\n"),
    ]),
    ("artifacts/docs/runbooks", "doc", "Operational runbooks.", [
        ("incident.md", "# Incident Runbook\n\n1. Detect\n2. Triage\n3. Mitigate\n4. Postmortem\n"),
    ]),
    ("artifacts/docs/decisions", "adr", "Architecture decision records.", [
        ("0001-example.md", "# ADR 0001: Example Decision\n\n- Status: proposed\n- Context:\n- Decision:\n- Consequences:\n"),
    ]),

    # --- taxonomies & catalogs ---
    ("artifacts/taxonomies", "taxonomy", "Component and capability taxonomies.", [
        ("components.json", "{\n  \"schema\": \"aether.components.v1\",\n  \"families\": []\n}\n"),
        ("capabilities.json", "{\n  \"schema\": \"aether.capabilities.v1\",\n  \"capabilities\": []\n}\n"),
    ]),
    ("artifacts/catalogs", "catalog", "Flat catalogs of known things.", [
        ("nature.txt", "# code | description\n"),
    ]),

    # --- ledgers & journals ---
    ("artifacts/ledgers", "ledger", "Append-only ledgers.", [
        ("ledger.jsonl", ""),
    ]),
    ("artifacts/journals", "journal", "Decision and change journals.", [
        ("journal.jsonl", ""),
    ]),

    # --- handoff & ops ---
    ("artifacts/handoff", "handoff", "Handoff notes between owners.", [
        ("HANDOFF.md", "# Handoff\n\n- From:\n- To:\n- State:\n- Open items:\n"),
    ]),
    ("artifacts/oncall", "oncall", "On-call rotations and escalation.", [
        ("oncall.yaml", "rotation: []\nescalation: []\n"),
    ]),

    # --- identity & crypto ---
    ("artifacts/keys", "key", "Public keys and key metadata.", [
        ("README.md", "# Keys\n\nPrivate keys are never stored in the repo.\n"),
    ]),
    ("artifacts/certs", "cert", "Certificates.", [
        (".gitkeep", ""),
    ]),
    ("artifacts/secrets", "secret", "Secret templates (never real secrets).", [
        (".env.example", "API_KEY=\nDATABASE_URL=\n"),
    ]),
]


def write(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return True


def main() -> int:
    created_dirs = 0
    created_files = 0
    skipped = 0

    for rel_dir, kind, description, stubs in ARTIFACT_SETS:
        d = ROOT / rel_dir
        d.mkdir(parents=True, exist_ok=True)
        created_dirs += 1

        # canonical description
        canonical = d / "CANONICAL.md"
        body = (
            f"# Artifact Set: `{rel_dir}`\n\n"
            f"- Kind: `{kind}`\n"
            f"- Description: {description}\n\n"
            f"## What belongs here\n\n"
            f"Files whose kind is `{kind}`. Every artifact set has a canonical\n"
            f"shape: a place for the file(s), a schema (if applicable), and a\n"
            f"provenance record. Keep this directory flat unless the set has more\n"
            f"than ~50 entries.\n"
        )
        if write(canonical, body, FORCE):
            created_files += 1
        else:
            skipped += 1

        for fname, content in stubs:
            if write(d / fname, content, FORCE):
                created_files += 1
            else:
                skipped += 1

    # top-level index
    index_lines = [
        "# Artifact Sets",
        "",
        f"Total sets: {len(ARTIFACT_SETS)}",
        "",
    ]
    for rel_dir, kind, description, _ in ARTIFACT_SETS:
        index_lines.append(f"- [`{rel_dir}`](./{rel_dir.replace('artifacts/', '')}) — `{kind}` — {description}")
    write(ROOT / "artifacts" / "INDEX.md", "\n".join(index_lines) + "\n", FORCE)

    print(f"artifact sets: {len(ARTIFACT_SETS)}")
    print(f"directories:   {created_dirs}")
    print(f"files written: {created_files}")
    print(f"files skipped: {skipped} (already existed; use --force to overwrite)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
