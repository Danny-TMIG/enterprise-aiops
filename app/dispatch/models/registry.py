from typing import Any


class ModelRegistry:
    def __init__(self):
        self.models = {}

    def register(self, name: str, model_info: dict[str, Any]):
        self.models[name] = model_info

    def get(self, name: str):
        return self.models.get(name, {"provider": "local", "path": name})

def get_registry() -> ModelRegistry:
    reg = ModelRegistry()
    reg.register("default", {"provider": "local", "path": "mlx-community/Qwen2.5-7B-Instruct-4bit"})
    return reg

class ModelRegistryStatus:
    def status(self) -> dict:
        return {"loaded": list(self.models.keys()) if hasattr(self, "models") else []}
