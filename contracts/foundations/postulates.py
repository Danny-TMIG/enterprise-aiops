"""ASF postulates — propositions posited as the basis for reasoning.

A postulate is stronger than a predicate and weaker than an axiom: it is
not assumed, but it is not yet proved. It is the shape of what the
implementation must establish. When proof arrives, a postulate becomes a
theorem. Until then, it is a claim under construction.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Postulate:
    id: str
    statement: str
    status: str  # "open" | "under_review" | "proved" | "refuted"
    dependencies: tuple[str, ...] = ()


POSTULATES = (
    Postulate(
        id="P1",
        statement="Every execution order has exactly one authorized issuer.",
        status="open",
    ),
    Postulate(
        id="P2",
        statement="Every terminal outcome is reconstructible from evidence alone.",
        status="open",
    ),
    Postulate(
        id="P3",
        statement="Duplicate delivery with a stable idempotency key produces one effect.",
        status="open",
    ),
    Postulate(
        id="P4",
        statement="Revocation dominates in-flight execution and is observable as a state transition.",
        status="open",
    ),
    Postulate(
        id="P5",
        statement="Cancellation is distinguishable from failure at every boundary.",
        status="open",
    ),
    Postulate(
        id="P6",
        statement="Delegation chains are non-amplifying: a child grant is a subset of its parent.",
        status="open",
    ),
    Postulate(
        id="P7",
        statement="Transformation cannot increase the disclosure level of an object.",
        status="open",
    ),
    Postulate(
        id="P8",
        statement="Cognition cannot construct an order that Govern would not have authorized.",
        status="open",
    ),
    Postulate(
        id="P9",
        statement="Compute cannot realize an order whose capability is outside the governed set.",
        status="open",
    ),
    Postulate(
        id="P10",
        statement="Every evidence claim has a source and an integrity reference.",
        status="open",
    ),
)


def is_open(p: Postulate) -> bool:
    return p.status in ("open", "under_review")


def is_proved(p: Postulate) -> bool:
    return p.status == "proved"


def open_postulates() -> list[Postulate]:
    return [p for p in POSTULATES if is_open(p)]
