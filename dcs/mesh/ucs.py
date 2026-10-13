"""The canonical UCS pipeline: spec → IR → generate → build → test → verify → publish.

Composes stages from the six taxonomies into the pipeline UCS documents.
"""

from dcs.mesh.behavior import pipeline  # pragma: no cover

UCS_STAGES = (
    # Bootstrap
    ("G0", "initialize"),
    # Parse the specification
    ("G1", "parse"),
    ("C1", "front-end"),
    # Resolve names, namespaces, types, dependencies
    ("R1", "identity"),
    ("R2", "namespace"),
    ("R3", "type"),
    ("R5", "dependency"),
    # Analyze and build the canonical IR
    ("G2", "analyze"),
    ("C2", "semantic"),
    ("C3", "canonical IR"),
    ("R6", "constraint"),
    # Optimize and transform IR
    ("C4", "analysis"),
    ("C5", "optimization"),
    ("G3", "transform"),
    # Synthesize artifacts
    ("G4", "synthesize"),
    ("G5", "emit"),
    # Build: codegen, link
    ("C6", "transformation"),
    ("C7", "back-end"),
    ("C8", "linking"),
    ("C10", "artifact"),
    # Verify: validate, verify, test
    ("G6", "validate"),
    ("C9", "verification"),
    ("G7", "execute"),
    ("K16", "conformance"),
    # Publish: package, sign, SBOM, release
    ("G11", "publish"),
    ("C15", "publication"),
    ("K17", "publication-kernel"),
    # Self-evolve
    ("G12", "self-evolve"),
    ("C16", "self-host"),
)

UCS = pipeline("UCS", *(sid for sid, _ in UCS_STAGES))
