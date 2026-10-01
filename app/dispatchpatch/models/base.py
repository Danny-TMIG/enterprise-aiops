class BaseModel:
    def __init__(self, name: str):
        self.name = name

    def generate(self, prompt: str) -> str:
        return f"Model {self.name} response to: {prompt}"
