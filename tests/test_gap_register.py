"""Gap register — every gap is either closed or documented as deferred."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "architecture" / "MODEL_GAP_CLOSURES.md"


def test_doc_exists():
    assert DOC.is_file()


def test_all_eleven_gaps_accounted_for():
    text = DOC.read_text()
    for n in range(1, 12):
        assert f"G{n}" in text, f"gap G{n} missing from closure doc"


def test_seven_gaps_closed():
    """G1-G5, G10, G11 are closed."""
    text = DOC.read_text()
    closed_section = text.split("## Deferred")[0]
    for gap in ("G1", "G2", "G3", "G4", "G5", "G10", "G11"):
        assert gap in closed_section, f"{gap} not in closed section"


def test_four_gaps_deferred():
    """G6-G9 are deferred, each with its blocking decision."""
    text = DOC.read_text()
    deferred_section = text.split("## Deferred")[1] if "## Deferred" in text else ""
    for gap, decision in (
        ("G6", "COG-DEC-009"),
        ("G7", "COG-DEC-010"),
        ("G8", "CMP-DEC-003"),
        ("G9", "COG-DEC-007"),
    ):
        assert gap in deferred_section, f"{gap} not in deferred section"
        assert decision in deferred_section, f"{decision} not cited for {gap}"
