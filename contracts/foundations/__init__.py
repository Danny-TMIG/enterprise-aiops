"""ASF foundations — axioms, postulates, primitives, invariants.

Layering:

    primitives   -- what the system is made of          (definitions)
    axioms       -- what is assumed without proof       (accept / reject)
    postulates   -- what is posited pending proof       (open / proved)
    invariants   -- what must hold in every state       (provable)
    predicates   -- what any given output must satisfy  (testable)

Everything above a layer depends on everything below it. Nothing below
depends on anything above.
"""
from contracts.foundations import primitives, axioms, postulates, invariants, layers

__all__ = ["primitives", "axioms", "postulates", "invariants", "layers"]
