#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    print("=== [Enterprise AIOps] Patching & Validation ===")
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root))

    # 1. Make torch optional in app/main.py if present
    main_py = repo_root / "app" / "main.py"
    if main_py.exists():
        content = main_py.read_text()
        if "import torch" in content and "try:\n    import torch" not in content:
            updated = content.replace(
                "import torch",
                "try:\n    import torch\nexcept ImportError:\n    torch = None"
            )
            main_py.write_text(updated)
            print("  -> Made torch import optional in app/main.py")

    print("\n[1/3] Verifying core Python imports...")
    try:
        from app.mesh import get_mesh
        print("  -> Core packages & mesh module verified successfully.")
    except Exception as e:
        print(f"  -> Import failed: {e}")
        sys.exit(1)

    print("\n[2/3] Initializing Mesh Runtime...")
    try:
        mesh = get_mesh()
        stats = mesh.graph.stats()
        print(f"  -> Mesh graph loaded successfully: {stats['nodes']} nodes, {stats['edges']} edges across {len(stats['kinds'])} node kinds.")
    except Exception as e:
        print(f"  -> Mesh initialization failed: {e}")
        sys.exit(1)

    print("\n[3/3] Executing test suite via python3 -m pytest...")
    # Explicitly pass PYTHONPATH=. to ensure all submodules resolve correctly
    env = dict(subprocess.os.environ)
    env["PYTHONPATH"] = str(repo_root)
    
    result = subprocess.run([sys.executable, "-m", "pytest", "-v"], cwd=str(repo_root), env=env)
    if result.returncode != 0:
        print("  -> Test suite reported failures.")
        sys.exit(result.returncode)
    
    print("\n=== All validation and test checks PASSED successfully! ===")

if __name__ == "__main__":
    main()
