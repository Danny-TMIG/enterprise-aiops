"""Parser and validator for the ASF Component Model grammar."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

GRAMMAR = Path(__file__).parent / "asf_component_grammar.ebnf"
COMPONENT_RE = re.compile(
    r"\b(GOV|CMP|COG)-(KRN|IAM|POL|INF|CAP|EVD|ADM|FED|CTL|TRU|RES|EXE|DAT|ECO|INT|CORE|REA|CMP|ASSUR)-\d{3}\b"
)
WP_RE = re.compile(r"\b(CMP-)?MATH-\d{3}\b")
DECISION_RE = re.compile(r"\b(GOV|CMP|COG)-DEC-\d{3}\b")


@dataclass
class GrammarIndex:
    components: dict = field(default_factory=lambda: {"GOV": set(), "CMP": set(), "COG": set()})
    work_packages: set = field(default_factory=set)
    open_decisions: set = field(default_factory=set)
    boundary_objects: list = field(default_factory=list)
    decision_outcomes: list = field(default_factory=list)
    assurance_states: list = field(default_factory=list)
    govern_invariants: list = field(default_factory=list)
    compute_invariants: list = field(default_factory=list)
    cognition_principles: list = field(default_factory=list)
    contract_invariants: list = field(default_factory=list)
    release_profiles: list = field(default_factory=list)
    gates: list = field(default_factory=list)


def parse_grammar(path=GRAMMAR):
    text = Path(path).read_text()
    idx = GrammarIndex()
    stripped = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)
    for m in COMPONENT_RE.finditer(stripped):
        idx.components[m.group(1)].add(m.group(0))
    for m in WP_RE.finditer(stripped):
        idx.work_packages.add(m.group(0))
    for m in DECISION_RE.finditer(stripped):
        idx.open_decisions.add(m.group(0))
    m = re.search(r"Object_Family_Name\s*=\s*(.*?);", stripped, re.DOTALL)
    if m:
        idx.boundary_objects = re.findall(r'"([A-Za-z]+)"', m.group(1))
    m = re.search(r"^Decision\s*=\s*(.*?);", stripped, re.MULTILINE | re.DOTALL)
    if m:
        idx.decision_outcomes = re.findall(r'"([A-Z_]+)"', m.group(1))
    m = re.search(r"^Assurance\s*=\s*(.*?);", stripped, re.MULTILINE | re.DOTALL)
    if m:
        idx.assurance_states = re.findall(r'"([A-Z_]+)"', m.group(1))
    for name, attr in [
        ("Govern_Invariant", "govern_invariants"),
        ("Compute_Invariant", "compute_invariants"),
        ("Cognition_Principle", "cognition_principles"),
        ("Contract_Invariant", "contract_invariants"),
    ]:
        m = re.search(rf"^{name}\s*=\s*(.*?);", stripped, re.MULTILINE | re.DOTALL)
        if m:
            setattr(idx, attr, re.findall(r'"([A-Za-z\-]+)"', m.group(1)))
    m = re.search(r"^Profile\s*=\s*(.*?);", stripped, re.MULTILINE | re.DOTALL)
    if m:
        idx.release_profiles = re.findall(r'"([MLSEG])"', m.group(1))
    m = re.search(r"^Gate\s*=\s*(.*?);", stripped, re.MULTILINE | re.DOTALL)
    if m:
        idx.gates = re.findall(r"\b(M[0-6])\b", m.group(1))
    return idx


def main():
    idx = parse_grammar()
    print("=== ASF Grammar Index ===")
    print()
    print(f"Govern components:    {len(idx.components['GOV'])}")
    print(f"Compute components:   {len(idx.components['CMP'])}")
    print(f"Cognition components: {len(idx.components['COG'])}")
    total = sum(len(v) for v in idx.components.values())
    print(f"Total components:     {total}")
    print()
    print(f"Boundary objects:     {len(idx.boundary_objects)}")
    print(f"Decision outcomes:    {len(idx.decision_outcomes)}")
    print(f"Assurance states:     {len(idx.assurance_states)}")
    print(f"Release profiles:     {len(idx.release_profiles)}")
    print(f"Gates:                {len(idx.gates)}")
    print(f"Work packages:        {len(idx.work_packages)}")
    print(f"Open decisions:       {len(idx.open_decisions)}")
    print(f"Govern invariants:    {len(idx.govern_invariants)}")
    print(f"Compute invariants:   {len(idx.compute_invariants)}")
    print(f"Cognition principles: {len(idx.cognition_principles)}")
    print(f"Contract invariants:  {len(idx.contract_invariants)}")
    print()
    assert total == 75
    assert len(idx.boundary_objects) == 19
    assert len(idx.decision_outcomes) == 5
    assert len(idx.assurance_states) == 6
    assert len(idx.govern_invariants) == 10
    assert len(idx.compute_invariants) == 12
    assert len(idx.cognition_principles) == 9
    assert len(idx.contract_invariants) == 5
    print("Grammar self-consistency: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
