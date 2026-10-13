from __future__ import annotations

from app.dispatch.verification.base import Prover, ProverResult


class Lean4Kernel(Prover):
    """Lean 4 kernel check.

    Two modes:
      * if `lean` is on PATH → shell out to `lean --run` on a temp file
      * otherwise            → structural check only (declared status)
    """
    name = "lean4-kernel"

    def available(self) -> bool:
        import shutil
        return shutil.which("lean") is not None

    def _prove(self, statement: str, context):
        lean_src = context.get("lean") or ""
        if not lean_src:
            return ProverResult(
                prover=self.name, status="INSUFFICIENT_DATA",
                error="no lean source supplied",
            )
        if not self.available():
            return ProverResult(
                prover=self.name, status="NOT_RUN",
                error="lean binary not on PATH",
                evidence=[{"type": "source", "value": lean_src[:200]}],
            )
        import os
        import subprocess
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False) as f:
            f.write(lean_src)
            path = f.name
        try:
            r = subprocess.run(["lean", path], capture_output=True,
                               text=True, timeout=30)
            ok = r.returncode == 0
            return ProverResult(
                prover=self.name,
                status="PASS" if ok else "FAIL",
                proof=lean_src,
                error=None if ok else (r.stderr or "")[:400],
                evidence=[{"type": "source", "value": lean_src[:200]}],
            )
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
