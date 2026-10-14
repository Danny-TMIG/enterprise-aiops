"""
Aether Semantic Layer Import Refactoring Utility
The Mark Intelligence Group - Universal Construction System (UCS)
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

IMPORT_MAPPINGS = {
    "from ag.ledger": "from ag.ledger",
    "import ag.ledger": "import ag.ledger",
    "from ax.model": "from ax.model",
    "import ax.model": "import ax.model",
    "from ag.healer": "from ag.healer",
    "import ag.healer": "import ag.healer",
    "from ag.verify": "from ag.verify",
    "import ag.verify": "import ag.verify",
    "from ac.router": "from ac.router",
    "import ac.router": "import ac.router",
}

def refactor_files():
    print("[*] Scanning monorepo for import refactoring...")
    modified_count = 0

    for path in ROOT.glob("**/*.py"):
        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue

        content = path.read_text(encoding="utf-8")
        updated_content = content

        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in updated_content:
                updated_content = updated_content.replace(old_import, new_import)

        if updated_content != content:
            path.write_text(updated_content, encoding="utf-8")
            print(f"    [UPDATED] {path.relative_to(ROOT)}")
            modified_count += 1

    print(f"\n[SUCCESS] Refactoring complete. Modified {modified_count} files.")

if __name__ == "__main__":
    refactor_files()
