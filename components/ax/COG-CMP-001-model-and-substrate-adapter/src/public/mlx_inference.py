"""
COG-CMP-001 — Live MLX Substrate Adapter
Provides direct inference bindings for local models on Apple Silicon via mlx-lm.
"""

from typing import Any, Dict, Optional
import time

try:
    from mlx_lm import generate, load
    HAS_MLX = True
except ImportError:
    HAS_MLX = False


class MLXInferenceBridge:
    def __init__(self, model_path: str = "mlx-community/Qwen2.5-7B-Instruct-4bit"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.loaded = False

    def initialize_model(self) -> None:
        if not HAS_MLX:
            raise ImportError("mlx-lm package is not installed in the virtual environment.")
        if not self.loaded:
            print(f"⚙️ [MLX] Loading local weights from {self.model_path} into Apple Silicon unified memory...")
            self.model, self.tokenizer = load(self.model_path)
            self.loaded = True
            print("✔ [MLX] Model loaded successfully.")

    def infer(self, prompt: str, max_tokens: int = 512, temp: float = 0.7) -> Dict[str, Any]:
        if not self.loaded:
            self.initialize_model()

        start_time = time.time()
        formatted_prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

        response_text = generate(
            self.model,
            self.tokenizer,
            prompt=formatted_prompt,
            max_tokens=max_tokens,
            verbose=False
        )

        duration = time.time() - start_time

        return {
            "status": "success",
            "model": self.model_path,
            "response": response_text.strip(),
            "metrics": {
                "duration_seconds": round(duration, 3),
                "tokens_generated": len(response_text.split())
            }
        }
