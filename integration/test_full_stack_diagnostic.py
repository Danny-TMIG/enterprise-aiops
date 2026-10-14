#!/usr/bin/env python3
"""Full-stack cross-layer sovereign integration diagnostic.

Exercises one path from each layer against the real component interfaces:
  AC: CMP-EVD-001 Observation and Telemetry — capture hardware facts
  AG: GOV-KRN-002 Governed State and Transition Engine — record a WORM
      state transition with envelope validation and hash chain
  AX: COG-CORE-001 Cognitive Runtime — run one cognitive operation
  Kernel 001: GovernanceRegistry — put two versions, verify chain
  Correlation: GOV-KRN-003 — open and close a correlation
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_full_sovereign_stack_pipeline() -> None:
    print("\n🔬 [DIAGNOSTIC] Initiating cross-layer sovereign integration test...")

    # 1. AC — Telemetry
    tel = load(
        "components/ac/CMP-EVD-001-observation-and-telemetry/src/public/telemetry.py",
        "ac_telemetry",
    )
    collector = tel.TelemetryCollector(source="dannys-macbook-m4max")
    event = collector.capture()
    assert event.event_id and event.metrics
    assert collector.verify(event.event_id) is True
    print(f"  ✔ [AC] Telemetry captured. platform={event.metrics['platform']}")

    # 2. AG — Governed state transition (WORM, envelope-validated, hash-chained)
    k2 = load(
        "components/ag/GOV-KRN-002-governed-state-and-transition-engine/src/public/engine.py",
        "ag_krn002",
    )
    envelope = {
        "schema_version": "1.0",
        "object_id": "diag-subject",
        "correlation_id": "diag-corr",
        "sovereign_domain": "tmig.local",
        "issuer": "integration-diagnostic",
        "purpose": "smoke",
        "classification": "internal",
        "event_time": "2026-10-14T00:00:00Z",
        "integrity": {"algorithm": "sha256", "digest": "0" * 64},
    }
    with k2.TransitionEngine() as engine:
        t1 = engine.record("diag-subject", "NEW", "OBSERVED", "diagnostic", "capture", envelope)
        t2 = engine.record("diag-subject", "OBSERVED", "SEALED", "diagnostic", "seal", envelope)
        assert t2.seq == 2 and t2.prev_hash == t1.chain_hash
        assert engine.verify_chain("diag-subject") is True
    print("  ✔ [AG] WORM state transition recorded and chain verified.")

    # 3. Kernel — Governance registry with immutable version chain
    k1 = load(
        "components/ag/GOV-KRN-001-governance-object-model-and-registry/src/public/registry.py",
        "ag_krn001",
    )
    with k1.GovernanceRegistry() as reg:
        a = reg.put("obj-1", "policy", {"rule": "deny"})
        b = reg.put("obj-1", "policy", {"rule": "allow"})
        assert a.version == 1 and b.version == 2
        assert b.prev_hash == a.chain_hash
        assert reg.verify_chain("obj-1") is True
    print("  ✔ [AG] Governance registry version chain verified.")

    # 4. Correlation
    k3 = load(
        "components/ag/GOV-KRN-003-decision-and-outcome-correlation/src/public/correlation.py",
        "ag_krn003",
    )
    with k3.CorrelationRegistry() as corr:
        c = corr.open("diag-corr", ["decision-1"])
        assert c.status == "OPEN"
        closed = corr.close_with_outcome("diag-corr", "outcome-1")
        assert closed.status == "CLOSED"
        assert corr.verify("diag-corr") is True
    print("  ✔ [AG] Decision/outcome correlation closed and verified.")

    # 5. AX — Cognitive runtime
    cog = load(
        "components/ax/COG-CORE-001-cognitive-runtime/src/public/runtime.py",
        "ax_cog",
    )
    runtime = cog.CognitiveRuntime(model_name="mlx-community/Qwen2.5-7B-Instruct-4bit")
    op = runtime.begin(f"Analyze system load: {event.metrics.get('cpu_load_percent')}%")
    result = runtime.execute(op.operation_id, "sovereign diagnostic")
    outcome = runtime.finish(op.operation_id)
    assert result and outcome.stages() == list(cog.CognitiveRuntime.STAGES)
    print(f"  ✔ [AX] Cognitive runtime completed {len(outcome.checkpoints)} stages.")

    print("💯 [SUCCESS] Full-stack cross-layer diagnostic test passed with zero errors.")


if __name__ == "__main__":
    test_full_sovereign_stack_pipeline()
