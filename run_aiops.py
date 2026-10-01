#!/usr/bin/env python3
import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def locate_asgi_module():
    """Recursively or directly search for main.py and determine its import path."""
    candidates = [
        Path("main.py"),
        Path("app/main.py"),
        Path("src/main.py"),
    ]
    for path in candidates:
        if path.exists():
            # Convert file path to dot notation (e.g., app/main.py -> app.main)
            parts = path.with_suffix("").parts
            return ".".join(parts)
    return None

def main():
    print("--------------------------------------------------")
    print("   Enterprise AIOps - Unified Launch & Diagnostics ")
    print("--------------------------------------------------")
    
    current_dir = Path.cwd()
    print(f"[*] Working Directory: {current_dir}")

    # 1. Locate module path
    module_name = locate_asgi_module()
    if not module_name:
        print("[!] Error: Could not locate 'main.py' in root, 'app/', or 'src/' directories.")
        sys.exit(1)
        
    target_app = f"{module_name}:app"
    print(f"[+] Discovered ASGI Target: {target_app}")

    # 2. Configure Python environment path
    env = os.environ.copy()
    env["PYTHONPATH"] = str(current_dir) + os.pathsep + env.get("PYTHONPATH", "")
    sys.path.insert(0, str(current_dir))

    # 3. Pre-flight import check
    print("[*] Running pre-flight module import check...")
    try:
        importlib.import_module(module_name)
        print("[+] Pre-flight check passed: Module imports cleanly.")
    except Exception as e:
        print(f"[!] Warning: Import check raised an exception: {e}")
        print("[*] Attempting to hand off to Uvicorn for detailed traceback...")

    # 4. Launch Uvicorn server
    cmd = ["uvicorn", target_app, "--reload", "--port", "8000"]
    print(f"[*] Executing: {' '.join(cmd)}\n")

    try:
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        print("\n[+] Service shutdown initiated by user. Exiting.")
    except subprocess.CalledProcessError as e:
        print(f"[!] Uvicorn exited with error code {e.returncode}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
