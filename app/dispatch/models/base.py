from enum import Enum
from typing import Any

from pydantic import BaseModel


class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    MLX = "mlx"

class ModelRequest(BaseModel):
    prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 512

class ModelResponse(BaseModel):
    text: str
    model: str
    usage: dict[str, Any] = {}
