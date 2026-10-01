from enum import Enum
from pydantic import BaseModel
from typing import Dict, Any

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
    usage: Dict[str, Any] = {}
