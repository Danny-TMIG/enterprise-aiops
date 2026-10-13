# 90_PROVENANCE_AND_SUPERSEDED_ARTIFACT_INDEX

Source package for `90_PROVENANCE_AND_SUPERSEDED_ARTIFACT_INDEX`.

## Files

- `__init__.py`
- `90_PROVENANCE_AND_SUPERSEDED_ARTIFACT_INDEX.py`

## Interface

- `Record` — dataclass with deterministic `digest()`
- `90ProvenanceAndSupersededArtifactIndex` — primary class with `emit()`, `records()`, `merkle_root()`

## Usage

    from 90_PROVENANCE_AND_SUPERSEDED_ARTIFACT_INDEX import 90ProvenanceAndSupersededArtifactIndex
    eng = 90ProvenanceAndSupersededArtifactIndex()
    eng.emit("event", {"k": "v"})
    print(eng.merkle_root())
