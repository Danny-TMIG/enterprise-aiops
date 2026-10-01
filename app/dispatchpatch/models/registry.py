from typing import Dict, Type
from app.dispatchpatch.models.base import BaseModel

class ModelRegistry:
    _models: Dict[str, Type[BaseModel]] = {}

    @classmethod
    def register(cls, name: str, model_cls: Type[BaseModel]):
        cls._models[name] = model_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseModel]:
        return cls._models.get(name, BaseModel)
