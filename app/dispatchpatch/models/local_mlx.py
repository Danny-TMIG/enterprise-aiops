from app.dispatchpatch.models.base import BaseModel


class LocalMLXModel(BaseModel):
    def generate(self, prompt: str) -> str:
        return f"[MLX Local] {super().generate(prompt)}"
