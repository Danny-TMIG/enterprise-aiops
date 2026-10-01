from pathlib import Path

print("=== 1. Fixing app/seed/runtime.py (Missing Any) ===")
p = Path("app/seed/runtime.py")
if p.exists():
    content = p.read_text()
    if "from typing import" in content and "Any" not in content:
        content = content.replace("from typing import ", "from typing import Any, ")
    elif "from typing import" not in content:
        content = "from typing import Any\n" + content
    p.write_text(content)
    print("[✔] Fixed Any import in app/seed/runtime.py")

print("=== 2. Fixing app/seed/seal.py (Missing DEFAULT_KEY) ===")
p = Path("app/seed/seal.py")
if p.exists():
    content = p.read_text()
    if "DEFAULT_KEY" not in content:
        content += "\n\nDEFAULT_KEY = b'enterprise_aiops_default_key_32bytes_min'\n"
        p.write_text(content)
        print("[✔] Added DEFAULT_KEY to app/seed/seal.py")

print("=== 3. Fixing app/generated/_all.py (Missing RUNNERS) ===")
p = Path("app/generated/_all.py")
p.parent.mkdir(parents=True, exist_ok=True)
if p.exists():
    content = p.read_text()
    if "RUNNERS" not in content:
        content += "\n\nRUNNERS = []\n"
        p.write_text(content)
        print("[✔] Added RUNNERS to app/generated/_all.py")
else:
    p.write_text("RUNNERS = []\n")
    print("[✔] Created app/generated/_all.py with RUNNERS")

print("=== 4. Fixing LocalMLXProvider inheritance in app/dispatch/models/local_mlx.py ===")
p = Path("app/dispatch/models/local_mlx.py")
if p.exists():
    content = p.read_text()
    # Remove direct enum inheritance clash
    content = content.replace("(ModelProvider)", "")
    p.write_text(content)
    print("[✔] Fixed LocalMLXProvider inheritance")

print("\nAll P2 import patches applied successfully!")
