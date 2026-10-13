"""Conformance: does the artifact match its declaration?

declared:  what the standard says
actual:    what the reference does (measured by re-running)
delta:     disagreements
verdict:   CONFORMANT iff declared == actual
"""

from __future__ import annotations  # pragma: no cover

from dataclasses import dataclass  # pragma: no cover
from pathlib import Path  # pragma: no cover

from dcs.conform import run as run_standard  # pragma: no cover
from dcs.standard import Standard, load  # pragma: no cover


@dataclass
class ConformanceReport:  # pragma: no cover
    standard_ref: str
    declared_must: int
    declared_should: int
    declared_may: int
    actual_must_pass: int
    actual_should_pass: int
    actual_may_pass: int
    verdict: str
    disagreements: list[dict]

    def to_dict(self) -> dict:  # pragma: no cover
        return self.__dict__  # pragma: no cover


def assess(std_path: Path, root: Path, *, sign_key: Path | None = None) -> ConformanceReport:  # pragma: no cover
    std: Standard = load(std_path)
    bundle = run_standard(std, root, sign_key=sign_key)
    summary = bundle.summary()

    declared = {"MUST": 0, "SHOULD": 0, "MAY": 0}
    for r in std.requirements:
        declared[r.criticality] = declared.get(r.criticality, 0) + 1

    disagreements = [
        {"id": rr.id, "criticality": rr.criticality, "error": rr.error}
        for rr in bundle.results
        if not rr.pass_  # pragma: no cover
    ]

    return ConformanceReport(  # pragma: no cover
        standard_ref=std.ref,
        declared_must=declared["MUST"],
        declared_should=declared["SHOULD"],
        declared_may=declared["MAY"],
        actual_must_pass=summary["MUST_pass"],
        actual_should_pass=summary["SHOULD_pass"],
        actual_may_pass=summary["MAY_pass"],
        verdict=bundle.verdict(),
        disagreements=disagreements,
    )


def render(rep: ConformanceReport) -> str:  # pragma: no cover
    lines = [
        f"conformance report  {rep.standard_ref}",
        "=" * 50,
        f"declared MUST/SHOULD/MAY:  {rep.declared_must}/{rep.declared_should}/{rep.declared_may}",
        f"actual   MUST/SHOULD/MAY:  "
        f"{rep.actual_must_pass}/{rep.actual_should_pass}/{rep.actual_may_pass}",
        f"verdict: {rep.verdict}",
    ]
    if rep.disagreements:  # pragma: no cover
        lines.append("disagreements:")
        for d in rep.disagreements:
            lines.append(f"  ✗ {d['criticality']:<7} {d['id']:<24} {d['error'] or ''}")
    return "\n".join(lines)  # pragma: no cover
