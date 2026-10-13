
from app.dispatchpatch.models.base import BaseModel


class ModelRegistry:
    _models: dict[str, type[BaseModel]] = {}

    @classmethod
    def register(cls, name: str, model_cls: type[BaseModel]):
        cls._models[name] = model_cls

    @classmethod
    def get(cls, name: str) -> type[BaseModel]:
        return cls._models.get(name, BaseModel)
