#!/usr/bin/env python3
"""
AAPCS64 & Apple ARM64 ABI Compliance Verification Pass.
Enforces 16-byte stack alignment, callee-saved register invariants, and link register preservation.
"""
import re
from pathlib import Path

CALLEE_SAVED_GPR = {f"x{i}" for i in range(19, 30)}
CALLEE_SAVED_SIMD = {f"v{i}" for i in range(8, 16)}

class FunctionContext:
    def __init__(self, name: str):
        self.name = name
        self.saved_gprs: set = set()
        self.restored_gprs: set = set()
        self.saved_simds: set = set()
        self.restored_simds: set = set()
        self.stack_allocated: int = 0
        self.has_nested_calls: bool = False
        self.saves_lr: bool = False
        self.violations: list[str] = []

def verify_assembly_file(filepath: Path) -> tuple[bool, list[dict]]:
    lines = filepath.read_text().splitlines()
    functions: dict[str, FunctionContext] = {}
    current_func = None

    label_re = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*):$")
    sub_sp_re = re.compile(r"sub\s+sp,\s+sp,\s*#?(\d+)", re.IGNORECASE)
    stp_re = re.compile(r"stp\s+([xX]\d+|[dD]\d+|[qQ]\d+),\s*([xX]\d+|[dD]\d+|[qQ]\d+),\s*\[sp", re.IGNORECASE)
    ldp_re = re.compile(r"ldp\s+([xX]\d+|[dD]\d+|[qQ]\d+),\s*([xX]\d+|[dD]\d+|[qQ]\d+),\s*\[sp", re.IGNORECASE)
    str_lr_re = re.compile(r"str\s+x30,\s*\[sp", re.IGNORECASE)
    bl_re = re.compile(r"\bbl\s+", re.IGNORECASE)

    for line in lines:
        line = line.strip()
        if not line or line.startswith("//") or line.startswith(";"):
            continue

        m_label = label_re.match(line)
        if m_label:
            func_name = m_label.group(1)
            current_func = FunctionContext(func_name)
            functions[func_name] = current_func
            continue

        if not current_func:
            continue

        m_sub = sub_sp_re.search(line)
        if m_sub:
            bytes_allocated = int(m_sub.group(1))
            current_func.stack_allocated = bytes_allocated
            if bytes_allocated % 16 != 0:
                current_func.violations.append(
                    f"Stack allocation {bytes_allocated} bytes violates 16-byte alignment requirement."
                )

        m_stp = stp_re.search(line)
        if m_stp:
            r1, r2 = m_stp.group(1).lower(), m_stp.group(2).lower()
            if r1 in CALLEE_SAVED_GPR: current_func.saved_gprs.add(r1)
            if r2 in CALLEE_SAVED_GPR: current_func.saved_gprs.add(r2)
            if r1 in CALLEE_SAVED_SIMD: current_func.saved_simds.add(r1)
            if r2 in CALLEE_SAVED_SIMD: current_func.saved_simds.add(r2)

        m_ldp = ldp_re.search(line)
        if m_ldp:
            r1, r2 = m_ldp.group(1).lower(), m_ldp.group(2).lower()
            if r1 in CALLEE_SAVED_GPR: current_func.restored_gprs.add(r1)
            if r2 in CALLEE_SAVED_GPR: current_func.restored_gprs.add(r2)
            if r1 in CALLEE_SAVED_SIMD: current_func.restored_simds.add(r1)
            if r2 in CALLEE_SAVED_SIMD: current_func.restored_simds.add(r2)

        if str_lr_re.search(line):
            current_func.saves_lr = True
        if bl_re.search(line):
            current_func.has_nested_calls = True

    audit_results = []
    global_passed = True

    for name, fn in functions.items():
        if fn.has_nested_calls and not fn.saves_lr:
            fn.violations.append("Non-leaf function makes branch-with-link (bl) but fails to save x30 (LR).")

        unrestored_gprs = fn.saved_gprs - fn.restored_gprs
        if unrestored_gprs:
            fn.violations.append(f"Callee-saved GPRs saved but not restored: {unrestored_gprs}")

        if fn.violations:
            global_passed = False

        audit_results.append({
            "function": name,
            "stack_allocated": fn.stack_allocated,
            "saves_lr": fn.saves_lr,
            "has_nested_calls": fn.has_nested_calls,
            "violations": fn.violations
        })

    return global_passed, audit_results
