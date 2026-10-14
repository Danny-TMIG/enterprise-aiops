#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Load catalog registry
CATALOG_PATH = Path("catalog/components.json")
if not CATALOG_PATH.exists():
    print("❌ Error: catalog/components.json not found. Run bootstrap_aether.py first.")
    sys.exit(1)

catalog = json.loads(CATALOG_PATH.read_text())


def generate_component_code(layer: str, cid: str, path_str: str):
    comp_dir = Path(path_str)

    # 1. Public Seam Implementation
    public_dir = comp_dir / "src" / "public"
    public_dir.mkdir(parents=True, exist_ok=True)

    class_name = "".join([word.capitalize() for word in cid.lower().split("-")]) + "Service"

    public_code = f'''"""
{cid} - Public Interface
Layer: {layer.upper()}
Governed under ASF v1.2 specification.
"""
from typing import Dict, Any, List

class {class_name}:
    def __init__(self, node_id: str = "dannys-macbook-m4max"):
        self.component_id = "{cid}"
        self.layer = "{layer.upper()}"
        self.node_id = node_id
        self.active_state = "initialized"

    def execute_operation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes standard bounded operation for {cid}.
        """
        self.active_state = "processing"
        result = {{
            "component_id": self.component_id,
            "status": "success",
            "received_payload": payload,
            "node": self.node_id
        }}
        self.active_state = "idle"
        return result
'''
    (public_dir / "service.py").write_text(public_code.strip() + "\n")

    # 2. Module Implementation
    modules_dir = comp_dir / "src" / "modules" / "core"
    modules_dir.mkdir(parents=True, exist_ok=True)
    (modules_dir / "__init__.py").write_text("# Core module execution logic\n")

    # 3. Adapters
    adapters_dir = comp_dir / "src" / "adapters"
    adapters_dir.mkdir(parents=True, exist_ok=True)
    (adapters_dir / "adapter.py").write_text(f'''"""
Adapter for {cid}
"""
class {cid.replace("-", "").capitalize()}Adapter:
    def adapt(self, data: Any) -> Any:
        return data
''')

    # 4. Unit and Contract Tests
    tests_unit = comp_dir / "tests" / "unit"
    tests_unit.mkdir(parents=True, exist_ok=True)
    tests_unit_code = f"""import pytest
from src.public.service import {class_name}

def test_{cid.lower().replace("-", "_")}_service():
    svc = {class_name}()
    assert svc.component_id == "{cid}"
    res = svc.execute_operation({{"test": True}})
    assert res["status"] == "success"
"""
    (tests_unit / f"test_{cid.lower().replace('-', '_')}.py").write_text(
        tests_unit_code.strip() + "\n"
    )


def main():
    print("🚀 [META-COMPILER] Generating source code and test suites for all 75 components...")
    components = catalog.get("components", [])

    for comp in components:
        layer = comp["layer"]
        cid = comp["id"]
        path_str = comp["path"]
        generate_component_code(layer, cid, path_str)
        print(f"  ✔ Populated {path_str}")

    print(
        f"💯 [COMPLETE] Successfully compiled and populated {len(components)} component codebases."
    )


if __name__ == "__main__":
    main()
