;; layer: schemas
;; dir:   schemas
FILE schemas/algorithms.schema.yaml
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
ENDFILE schemas/algorithms.schema.yaml
FILE schemas/capabilities.schema.yaml
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
ENDFILE schemas/capabilities.schema.yaml
FILE schemas/components.schema.yaml
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
ENDFILE schemas/components.schema.yaml
FILE schemas/ledger_entry.schema.yaml
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
ENDFILE schemas/ledger_entry.schema.yaml
FILE schemas/manifest.schema.yaml
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
ENDFILE schemas/manifest.schema.yaml
FILE schemas/nature_catalog.schema.yaml
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
ENDFILE schemas/nature_catalog.schema.yaml
FILE schemas/registry_envelope.schema.yaml
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
ENDFILE schemas/registry_envelope.schema.yaml
