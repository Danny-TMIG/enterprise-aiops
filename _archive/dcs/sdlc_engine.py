# Invariant SDLC Manifest Engine
import json
from pathlib import Path
from typing import Any


class SdlcEngine:
    def __init__(
        self,
        manifest_path: str = "dcs/standards/sdlc.json",
        uke_path: str = "dcs/standards/uke_registry.json",
    ):
        self.manifest_path = Path(manifest_path)
        self.uke_path = Path(uke_path)

    def load_manifest(self) -> list[dict[str, Any]]:
        if not self.manifest_path.exists():
            return []
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return json.load(f).get("requirements", [])

    def map_to_uke_primitive(self, process_id: str, primitive_id: str) -> dict[str, Any]:
        if not self.uke_path.exists():
            return {"status": "MAPPING_UNVERIFIED"}
        with open(self.uke_path, "r", encoding="utf-8") as f:
            uke_data = json.load(f)
        primitive = uke_data.get("primitives", {}).get(primitive_id)
        if not primitive:
            return {"status": "MAPPING_REJECTED"}
        return {
            "status": "MAPPING_VERIFIED",
            "process_id": process_id,
            "uke_id": primitive_id,
            "axis": primitive["axis"],
            "sub_family": primitive["sub_family"],
            "description": primitive["desc"],
        }
