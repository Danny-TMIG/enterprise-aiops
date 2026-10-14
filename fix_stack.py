from pathlib import Path


def fix_repository():
    print("🔧 [FIX] Ensuring all component directories are valid python packages...")

    # 1. Add __init__.py files recursively in components/
    components_root = Path("components")
    if components_root.exists():
        for path in components_root.rglob("*"):
            if path.is_dir():
                init_file = path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("# Auto-generated package init\n")

    print("  ✔ Package init files verified across components.")

    # 2. Write the robust diagnostic test file
    diagnostic_path = Path("integration/test_full_stack_diagnostic.py")
    diagnostic_path.parent.mkdir(parents=True, exist_ok=True)

    diagnostic_code = '''#!/usr/bin/env python3
"""
Full-Stack Sovereign Diagnostic Test (Direct Execution Version)
Integrates AC (Telemetry), AG (Govern & State Engine), and AX (Cognition).
"""
import sys
import importlib.util
from pathlib import Path

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod

root = Path(__file__).resolve().parent.parent

# 1. Load AIOps Engine
aiops_engine_path = root / "src" / "aiops_platform_metadusa_cell" / "engine.py"
aiops_mod = load_module_from_path("aiops_engine", aiops_engine_path)
AIOpsEngine = aiops_mod.AIOpsEngine

# 2. Load AC Telemetry Collector
ac_path = root / "components" / "ac" / "CMP-EVD-001-observation-and-telemetry" / "src" / "public" / "telemetry.py"
ac_mod = load_module_from_path("ac_telemetry", ac_path)
TelemetryCollector = ac_mod.TelemetryCollector

# 3. Load AG State Transition Engine
ag_path = root / "components" / "ag" / "GOV-KRN-002-governed-state-and-transition-engine" / "src" / "public" / "engine.py"
ag_mod = load_module_from_path("ag_engine", ag_path)
StateTransitionEngine = ag_mod.StateTransitionEngine

# 4. Load AX Cognitive Runtime
ax_path = root / "components" / "ax" / "COG-CORE-001-cognitive-runtime" / "src" / "public" / "runtime.py"
ax_mod = load_module_from_path("ax_runtime", ax_path)
CognitiveRuntime = ax_mod.CognitiveRuntime

def test_full_sovereign_stack_pipeline():
    print("\\n🔬 [DIAGNOSTIC] Initiating cross-layer sovereign integration test...")

    # 1. Low-Level Compute (AC): Collect native telemetry
    telemetry_collector = TelemetryCollector(node_id="dannys-macbook-m4max")
    raw_metrics = telemetry_collector.collect_metrics()
    assert raw_metrics["node_id"] == "dannys-macbook-m4max"
    assert "cpu_load_percent" in raw_metrics["metrics"]
    print("  ✔ [AC] Telemetry successfully captured from hardware substrate.")

    # 2. Govern Layer (AG): Process state transition and append to WORM ledger
    governance_engine = StateTransitionEngine()
    transition_record = governance_engine.transition(
        object_id="GOV-SYS-CELL-01",
        from_state="IDLE",
        to_state="PROCESSING_TELEMETRY",
        actor="dannys-macbook.internal"
    )
    assert transition_record["veto_check"] is True
    assert transition_record["to_state"] == "PROCESSING_TELEMETRY"
    print("  ✔ [AG] Governance policy and WORM state transition verified.")

    # 3. Cognition Layer (AX): Execute cognitive evaluation over the telemetry & state
    cog_runtime = CognitiveRuntime(model_name="mlx-community/Qwen2.5-7B-Instruct-4bit")
    cognitive_output = cog_runtime.execute_prompt(f"Analyze system load: {raw_metrics['metrics']['cpu_load_percent']}%")
    assert "LOCAL-MLX" in cognitive_output
    print("  ✔ [AX] Cognitive runtime successfully processed state.")

    # 4. In-RAM AIOps Engine Verification
    aiops_engine = AIOpsEngine()
    buffered_count = aiops_engine.ingest(raw_metrics)
    assert buffered_count == 1
    status = aiops_engine.status()
    assert status["buffered_metrics"] == 1
    print("  ✔ [CELL] In-RAM telemetry buffer verified successfully.")
    print("💯 [SUCCESS] Full-stack cross-layer diagnostic test passed with zero errors.")

if __name__ == "__main__":
    test_full_sovereign_stack_pipeline()
'''
    diagnostic_path.write_text(diagnostic_code)
    print("  ✔ Rewrote integration/test_full_stack_diagnostic.py cleanly.")


if __name__ == "__main__":
    fix_repository()
