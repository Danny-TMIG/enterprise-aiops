;; artifact: manifest_schema
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
