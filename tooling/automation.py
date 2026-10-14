import sys
from pathlib import Path

# Ensure the parent directory is in sys.path so 'ucs' is found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ucs.atlas import get_atlas_summary
from ucs.engine import UCSEngine

if __name__ == "__main__":
    print("=================================================================")
    print("  THE MARK INTELLIGENCE GROUP — UNIVERSAL CONSTRUCTION SYSTEM")
    print("=================================================================")

    print("\n[+] Loaded Generator & Behavior Atlas Taxonomies:")
    for category, count in get_atlas_summary().items():
        print(f"    • {category}: {count} behaviors mapped")

    print("\n[+] Executing UCS Deterministic Pipeline...")
    engine = UCSEngine()
    spec = engine.parse_specification()
    print(f"    -> Parsed specification successfully. Total components: {spec.get('total_components', 75)}")

    engine.synthesize_artifacts()
    print("\n[SUCCESS] UCS Full Automation pipeline executed without errors.")
