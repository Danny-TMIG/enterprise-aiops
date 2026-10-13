"""The filter predicate.

Emit only if the teacher's output passes the SAME verifier the
compiler uses, and the student's output fails the same verifier.
We re-run the verifier here; we do not trust the probe's cache.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.delta.delta import Delta


@dataclass
class FilterDecision:
    accept: bool
    reason: str


def filter_delta(d: Delta, workload) -> FilterDecision:
    if not d.is_signal:
        return FilterDecision(False, f"quadrant={d.quadrant.value}")

    teacher = d.teacher
    student = d.student
    if teacher is None or student is None:
        return FilterDecision(False, "missing teacher or student")

    v_teacher = workload.verifier.verify(d.input_value, teacher.output)
    v_student = workload.verifier.verify(d.input_value, student.output)

    if not v_teacher.passed:
        return FilterDecision(False, "teacher no longer passes")
    if v_student.passed:
        return FilterDecision(False, "student unexpectedly passes")

    return FilterDecision(True,
                          f"teacher={v_teacher.state} "
                          f"student={v_student.state}")
