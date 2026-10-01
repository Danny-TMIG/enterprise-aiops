import logging
from typing import Dict, Any, Tuple
from mlx_lm import load, generate

logging.basicConfig(level=logging.INFO)

class OrthogonalMoAOrchestrator:
    def __init__(self):
        # 8-Expert Orthogonal Mapping across Apple M4 Max unified memory
        self.expert_models: Dict[str, str] = {
            "router": "mlx-community/Qwen2.5-7B-Instruct-4bit",
            "coder": "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
            "topology": "mlx-community/DeepSeek-R1-Distill-Qwen-7B-4bit",
            "verifier": "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
            "security": "mlx-community/Qwen2.5-7B-Instruct-4bit",
            "diagnostic": "mlx-community/Mistral-7B-Instruct-v0.3-4bit",
            "critic": "mlx-community/Qwen2.5-7B-Instruct-4bit",
            "schema": "mlx-community/Qwen2.5-7B-Instruct-4bit",
        }
        self.loaded_cache: Dict[str, Tuple[Any, Any]] = {}

    def get_expert(self, role: str):
        if role not in self.loaded_cache:
            model_id = self.expert_models.get(role, self.expert_models["router"])
            logging.info(f"[+] Loading orthogonal expert '{role}' ({model_id}) into M4 Max unified memory...")
            model, tokenizer = load(model_id)
            self.loaded_cache[role] = (model, tokenizer)
        return self.loaded_cache[role]

    def dispatch(self, role: str, prompt: str, max_tokens: int = 512) -> str:
        model, tokenizer = self.get_expert(role)
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        response = generate(model, tokenizer, prompt=formatted_prompt, verbose=False, max_tokens=max_tokens)
        return response
