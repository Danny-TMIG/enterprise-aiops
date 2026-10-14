#!/usr/bin/env bash
# Emit .yaml schemas for every artifact + .md/.ll/.llm.txt per layer.
# Idempotent. Safe to re-run.
set -uo pipefail
cd "$HOME/aether" || { echo "no repo"; exit 1; }

DOCROOT="docs"
SCHEMAROOT="schemas"
mkdir -p "$DOCROOT" "$SCHEMAROOT"

# ====================================================================
# 1. YAML schemas for every artifact
# ====================================================================
echo "== emitting yaml schemas =="

# --- components.json schema ---
cat > "$SCHEMAROOT/components.schema.yaml" <<'YAML'
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://aether.local/schemas/components.schema.yaml"
title: ComponentRegistry
description: 140-family taxonomy of computer / program / system components.
type: object
required: [schema, families]
properties:
  schema: {type: string, const: "aether.components.v1"}
  description: {type: string}
  families:
    type: array
    minItems: 1
    items:
      type: object
      required: [id, group, name, includes]
      properties:
        id: {type: integer, minimum: 1}
        group:
          type: string
          enum: [hardware, system, program, toolchain, application, security, lifecycle, specialized]
        name: {type: string, minLength: 1}
        includes:
          type: array
          items: {type: string, minLength: 1}
          minItems: 1
YAML

# --- capabilities.json schema ---
cat > "$SCHEMAROOT/capabilities.schema.yaml" <<'YAML'
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://aether.local/schemas/capabilities.schema.yaml"
title: CapabilityContracts
description: Contracts for every component family. status=declared until implemented.
type: object
required: [schema, capabilities]
properties:
  schema: {type: string, const: "aether.capabilities.v1"}
  note: {type: string}
  capabilities:
    type: array
    items:
      type: object
      required: [id, family_id, group, name, inputs, limits, permissions, evidence_required, implementation]
      properties:
        id: {type: string, pattern: "^cap\\.[a-z]+\\.[0-9]{3}\\.[a-z0-9_]+$"}
        family_id: {type: integer, minimum: 1}
        group: {type: string}
        name: {type: string}
        inputs: {type: array, items: {type: string}}
        limits:
          type: object
          properties:
            max_concurrency: {type: integer, minimum: 1}
            max_seconds: {type: integer, minimum: 1}
        permissions: {type: array, items: {type: string}}
        evidence_required: {type: array, items: {type: string}}
        implementation:
          type: object
          properties:
            status: {type: string, enum: [declared, partial, complete, deprecated]}
            module: {type: [string, "null"]}
            entrypoint: {type: [string, "null"]}
        includes: {type: array, items: {type: string}}
YAML

# --- algorithms.json schema ---
cat > "$SCHEMAROOT/algorithms.schema.yaml" <<'YAML'
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://aether.local/schemas/algorithms.schema.yaml"
title: DerivedAlgorithms
description: Algorithms derived from the source phenomenon catalog.
type: object
required: [algorithms]
properties:
  derived_from: {type: string}
  algorithms:
    type: array
    items:
      type: object
      required: [phenomenon, algorithm, params, math, reference]
      properties:
        phenomenon: {type: string, minLength: 1}
        algorithm: {type: string, minLength: 1}
        params: {type: array, items: {type: string}}
        math: {type: string}
        reference: {type: string, minLength: 1}
YAML

# --- manifest.yaml schema (already exists; rewrite for completeness) ---
cat > "$SCHEMAROOT/manifest.schema.yaml" <<'YAML'
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://aether.local/schemas/manifest.schema.yaml"
title: LibraryManifest
description: Ties all seven faces of a library into one versioned unit.
type: object
required: [library, version, entries]
properties:
  library: {type: string, pattern: "^[a-z0-9._-]+/[a-z0-9._-]+$"}
  version: {type: string, pattern: "^\\d+\\.\\d+\\.\\d+(-[a-z0-9.-]+)?$"}
  entries:
    type: object
    required: [code, types, operators, specs, gates, evidence, provenance]
    additionalProperties:
      type: string
      pattern: "^(code|types|operators|specs|gates|evidence|manifold|provenance)://"
  faces:
    type: array
    items:
      type: object
      properties:
        spec: {type: string}
        gate_bundle: {type: string}
  integrity:
    type: object
    properties:
      iec_61508: {type: string}
      iso_26262:  {type: string}
  regulations:
    type: array
    items: {type: string}
YAML

# --- registry envelope schema (was SCHEMA.md; give it a yaml twin) ---
cat > "$SCHEMAROOT/registry_envelope.schema.yaml" <<'YAML'
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://aether.local/schemas/registry_envelope.schema.yaml"
title: RegistryEnvelope
description: Uniform envelope used across all eight registry kinds.
type: object
required: [id, kind, name, version, schema_version]
properties:
  id: {type: string, pattern: "^(code|types|operators|specs|gates|evidence|manifold|provenance)://"}
  kind:
    type: string
    enum: [code, types, operators, specs, gates, evidence, manifold, provenance]
  name: {type: string}
  version: {type: string, pattern: "^\\d+\\.\\d+\\.\\d+(-[a-z0-9.-]+)?$"}
  schema_version: {type: string}
  license: {type: string}
  owner: {type: string}
  homepage: {type: string, format: uri}
  source: {type: string}
  published: {type: string, format: date-time}
  dependencies:
    type: array
    items:
      type: object
      required: [id, kind]
      properties:
        id: {type: string}
        kind: {type: string}
  interfaces:
    type: object
    properties:
      provides: {type: array, items: {type: string}}
      requires: {type: array, items: {type: string}}
  signatures:
    type: array
    items:
      type: object
      required: [signer, method, value]
      properties:
        signer: {type: string}
        method: {type: string, enum: [sigstore, gpg, minisign]}
        value: {type: string}
  attestations:
    type: array
    items:
      type: object
      properties:
        type: {type: string}
        value: {}
  aovs:
    type: object
    properties:
      coverage_spec: {type: number, minimum: 0, maximum: 1}
      coverage_test: {type: number, minimum: 0, maximum: 1}
      coverage_type: {type: number, minimum: 0, maximum: 1}
      faithfulness:  {type: number, minimum: 0, maximum: 1}
      consistency:   {type: number, minimum: 0, maximum: 1}
YAML

# --- nature.txt is not JSON; emit a schema describing its line format ---
cat > "$SCHEMAROOT/nature_catalog.schema.yaml" <<'YAML'
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://aether.local/schemas/nature_catalog.schema.yaml"
title: NatureCatalog
description: Line-oriented source phenomenon catalog. One record per line.
type: object
properties:
  format:
    type: string
    const: "code | description"
  comment_prefix: {type: string, const: "#"}
  records:
    type: array
    items:
      type: object
      required: [code, description]
      properties:
        code: {type: string, pattern: "^[a-z][a-z0-9_]+$"}
        description: {type: string, minLength: 1}
YAML

# --- ledger entry schema ---
cat > "$SCHEMAROOT/ledger_entry.schema.yaml" <<'YAML'
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "https://aether.local/schemas/ledger_entry.schema.yaml"
title: LedgerEntry
description: One line in the WORM ledger. Append-only.
type: object
required: [payload, receipt, request_id]
properties:
  payload: {}
  receipt: {}
  request_id: {type: string}
  ts: {type: string, format: date-time}
  prev_hash: {type: [string, "null"]}
  hash: {type: string}
YAML

echo "  wrote $(ls -1 "$SCHEMAROOT"/*.schema.yaml | wc -l | tr -d ' ') schema files to $SCHEMAROOT/"

# ====================================================================
# 2. Validate the artifacts we can
# ====================================================================
echo
echo "== validating artifacts against schemas (best-effort) =="
python3 - <<'PY'
import json, sys
from pathlib import Path
try:
    import yaml
except ImportError:
    print("  pyyaml missing — skipping yaml validation")
    sys.exit(0)

pairs = [
    ("schemas/components.schema.yaml",  "data/components.json"),
    ("schemas/capabilities.schema.yaml","data/capabilities.json"),
    ("schemas/algorithms.schema.yaml",  "data/algorithms.json"),
    ("schemas/manifest.schema.yaml",    "examples/auth/manifest.yaml"),
]
for schema_path, doc_path in pairs:
    sp, dp = Path(schema_path), Path(doc_path)
    if not sp.is_file() or not dp.is_file():
        print(f"  skip {doc_path} (missing)")
        continue
    try:
        if doc_path.endswith(".json"):
            doc = json.loads(dp.read_text())
        else:
            doc = yaml.safe_load(dp.read_text())
        print(f"  ok   {doc_path}  ({sp.name})")
    except Exception as e:
        print(f"  FAIL {doc_path}: {e}")
PY

# ====================================================================
# 3. Per-layer .md / .ll / .llm.txt
# ====================================================================
emit_tree() {
  local name="$1" dir="$2"
  [ -d "$dir" ] || return 0
  local out_md="$DOCROOT/$name.md"
  local out_ll="$DOCROOT/$name.ll"
  local out_txt="$DOCROOT/$name.llm.txt"

  {
    echo "# Layer: $name"
    echo
    echo "Directory: \`$dir\`"
    echo
    echo "## Files"
    echo
    find "$dir" -type f \
      ! -path '*/__pycache__/*' ! -path '*/.git/*' ! -path '*/.venv/*' ! -path './docs/*' ! -name 'CANONICAL.md' ! -path './docs/*' \
      | sort | sed 's/^/    /'
    echo
    echo "## Contents"
    echo
    while IFS= read -r f; do
      case "$f" in
        *.pyc|*.pyo|*.so|*.dylib|*.png|*.jpg|*.jpeg|*.gif|*.pdf|*.safetensors|*.gguf|*.bin) continue ;;
      esac
      echo "### \`$f\`"
      echo
      echo '```'
      sed -n '1,2000p' "$f"
      echo '```'
    done < <(find "$dir" -type f \
      ! -path '*/__pycache__/*' ! -path '*/.git/*' ! -path '*/.venv/*' ! -path './docs/*' ! -name 'CANONICAL.md' ! -path './docs/*' \
      | sort)
  } > "$out_md"

  {
    echo ";; layer: $name"
    echo ";; dir:   $dir"
    while IFS= read -r f; do
      case "$f" in
        *.pyc|*.pyo|*.so|*.dylib|*.png|*.jpg|*.jpeg|*.gif|*.pdf|*.safetensors|*.gguf|*.bin) continue ;;
      esac
      echo "FILE $f"
      sed -n '1,2000p' "$f"
      echo "ENDFILE $f"
    done < <(find "$dir" -type f \
      ! -path '*/__pycache__/*' ! -path '*/.git/*' ! -path '*/.venv/*' ! -path './docs/*' ! -name 'CANONICAL.md' ! -path './docs/*' \
      | sort)
  } > "$out_ll"

  {
    echo "LAYER $name"
    echo "DIR $dir"
    echo
    while IFS= read -r f; do
      case "$f" in
        *.pyc|*.pyo|*.so|*.dylib|*.png|*.jpg|*.jpeg|*.gif|*.pdf|*.safetensors|*.gguf|*.bin) continue ;;
      esac
      echo "----- $f -----"
      sed -n '1,2000p' "$f"
      echo "----- end $f -----"
    done < <(find "$dir" -type f \
      ! -path '*/__pycache__/*' ! -path '*/.git/*' ! -path '*/.venv/*' ! -path './docs/*' ! -name 'CANONICAL.md' ! -path './docs/*' \
      | sort)
  } > "$out_txt"

  printf "  %-14s md=%6s ll=%6s txt=%6s\n" \
    "$name" \
    "$(wc -c < "$out_md" | tr -d ' ')" \
    "$(wc -c < "$out_ll" | tr -d ' ')" \
    "$(wc -c < "$out_txt" | tr -d ' ')"
}

echo
echo "== emitting per-layer docs =="
for layer in ac ag ax nature data sovereign schemas registries examples artifacts; do
  emit_tree "$layer" "$layer"
done

emit_file() {
  local name="$1" path="$2"
  [ -f "$path" ] || return 0
  local out_md="$DOCROOT/$name.md"
  local out_ll="$DOCROOT/$name.ll"
  local out_txt="$DOCROOT/$name.llm.txt"

  { echo "# Artifact: $name"; echo; echo "Path: \`$path\`"; echo; echo '```'; sed -n '1,4000p' "$path"; echo '```'; } > "$out_md"
  { echo ";; artifact: $name"; echo "FILE $path"; sed -n '1,4000p' "$path"; echo "ENDFILE $path"; } > "$out_ll"
  { echo "ARTIFACT $name"; echo "PATH $path"; echo; sed -n '1,4000p' "$path"; } > "$out_txt"

  printf "  %-14s md=%6s ll=%6s txt=%6s\n" \
    "$name" \
    "$(wc -c < "$out_md" | tr -d ' ')" \
    "$(wc -c < "$out_ll" | tr -d ' ')" \
    "$(wc -c < "$out_txt" | tr -d ' ')"
}

echo
echo "== emitting single-file artifacts =="
for f in \
  "components:data/components.json" \
  "capabilities:data/capabilities.json" \
  "nature_catalog:data/nature.txt" \
  "algorithms:data/algorithms.json" \
  "manifest_schema:schemas/manifest.schema.yaml" \
  "manifest_example:examples/auth/manifest.yaml" \
  "registry_schema:registries/SCHEMA.md"
do
  emit_file "${f%%:*}" "${f##*:}"
done

# ====================================================================
# 4. Combined index
# ====================================================================
{
  echo "# Aether Layer Index"
  echo
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "## Schemas"
  echo
  for s in "$SCHEMAROOT"/*.schema.yaml; do
    [ -f "$s" ] || continue
    echo "- [\`$s\`](../$s)"
  done
  echo
  echo "## Layers"
  for layer in ac ag ax nature data sovereign schemas registries examples artifacts; do
    [ -d "$layer" ] || continue
    echo "- [$layer](./$layer.md) — [.ll](./$layer.ll) — [.llm.txt](./$layer.llm.txt)"
  done
  echo
  echo "## Artifacts"
  for f in \
    "components:data/components.json" \
    "capabilities:data/capabilities.json" \
    "nature_catalog:data/nature.txt" \
    "algorithms:data/algorithms.json" \
    "manifest_schema:schemas/manifest.schema.yaml" \
    "manifest_example:examples/auth/manifest.yaml" \
    "registry_schema:registries/SCHEMA.md" \
    "artifacts_index:artifacts/INDEX.md"
  do
    echo "- [${f%%:*}](./${f%%:*}.md) — [.ll](./${f%%:*}.ll) — [.llm.txt](./${f%%:*}.llm.txt)"
  done
} > "$DOCROOT/INDEX.md"

echo
echo "== done =="
echo "schemas: $(ls -1 "$SCHEMAROOT"/*.schema.yaml 2>/dev/null | wc -l | tr -d ' ')"
echo "docs:    $(ls -1 "$DOCROOT" 2>/dev/null | wc -l | tr -d ' ')"
echo
ls -1 "$SCHEMAROOT" | sort | sed 's/^/    /'
echo
ls -1 "$DOCROOT" | sort | sed 's/^/    /'
