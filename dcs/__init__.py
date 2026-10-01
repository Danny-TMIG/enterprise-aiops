"""dcs — declarative conformance standard + evidence toolchain.

Layers (outer → inner):
    standard     declarative spec (JSON, schema-validated)
    requirements atomic MUST/SHOULD/MAY clauses
    tests        executable functions referenced by dotted path
    evidence     content-addressed record of one conformance run
    transparency append-only Merkle log of every run

No layer trusts the layer above. Evidence can be re-verified against
a standard by a third party with only: standard file, evidence file,
reference implementation, and optional public key.
"""
__version__ = "1.0.0"
