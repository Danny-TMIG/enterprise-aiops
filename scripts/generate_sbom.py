import json
from pathlib import Path

Path("dist/sbom.json").write_text(json.dumps({"name": "sbom"}))
