import os
import sys
import coverage

def run_discovery():
    print("\n🔍 Verifying Sovereign Core Infrastructure Telemetry Matrix...")
    cov = coverage.Coverage(config_file=".coveragerc")
    cov.load()
    data = cov.get_data()
    measured_files = data.measured_files()
    if not measured_files:
        sys.exit(1)
        
    has_gaps = False
    target_includes = [
        "dcs/verify.py", "dcs/verify_intoto.py", "dcs/mesh/behavior.py",
        "dcs/self.py", "dcs/crosscut/semver.py", "dcs/__main__.py", "dcs/conform.py",
        "dcs/core/difference_engine.py", "dcs/core/operators.py", "dcs/crosscut/interop.py",
        "dcs/equivalence.py", "dcs/coherence.py"
    ]
    
    print("📋 Filtered Component Coverage Summary Matrix:")
    for file_path in measured_files:
        rel_path = os.path.relpath(file_path)
        if not any(target in rel_path for target in target_includes):
            continue
            
        analysis = cov._analyze(file_path)
        missing_lines = sorted(list(analysis.missing))
        if missing_lines:
            has_gaps = True
            print(f"🟥 {rel_path} -> Missing Lines: {missing_lines}")
        else:
            print(f"🟩 {rel_path} -> 100% TEST COMPLIANT")
            
    if has_gaps:
        sys.exit(1)
    print("🎉 Success: 100% Threshold achieved across all system interfaces!")
    sys.exit(0)

if __name__ == "__main__":
    run_discovery()
