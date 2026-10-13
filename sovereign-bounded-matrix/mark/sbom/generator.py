import json
import time

def generate_sbom():
    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "version": 1,
        "metadata": {
            "timestamp": time.time(),
            "component": {
                "name": "Aether Sovereign Fabric",
                "version": "1.1.0",
                "type": "framework"
            }
        },
        "components": [
            {"name": "fastapi", "version": "0.110.0", "type": "library"},
            {"name": "pydantic", "version": "2.6.0", "type": "library"},
            {"name": "mlx", "version": "0.10.0", "type": "library"}
        ]
    }
    return json.dumps(sbom, indent=2)

if __name__ == "__main__":
    print(generate_sbom())
