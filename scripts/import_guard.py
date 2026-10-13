import importlib
import sys

PROTECTED_MODULES = ["numpy", "fastapi", "uvicorn", "pydantic", "networkx", "redis", "mlx"]

def audit_imports():
    failed = False
    print("=== Auditing Protected Python Modules ===")
    for mod_name in PROTECTED_MODULES:
        try:
            mod = importlib.import_module(mod_name)
            origin = getattr(mod, "__file__", "built-in / namespace")
            print(f"[PASS] {mod_name:<12} -> {origin}")
        except Exception as e:
            print(f"[FAIL] {mod_name:<12} -> Error: {e}")
            failed = True
    if failed:
        print("\n[ERROR] Module missing or shadowed!")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All core modules verified cleanly.")

if __name__ == "__main__":
    audit_imports()
