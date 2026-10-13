from __future__ import annotations

import os

from app.dispatch.models.base import ModelProvider, ModelRequest, ModelResponse


class DeepSeekProvider(ModelProvider):
    """DeepSeek is OpenAI-compatible; we reuse the OpenAI SDK with a
    different base_url. No separate SDK needed."""
    name = "deepseek"
    default_model = "deepseek-chat"

    def available(self) -> bool:
        if not os.environ.get("DEEPSEEK_API_KEY"):
            return False
        try:
            import openai  # noqa: F401
            return True
        except Exception:
            return False

    def _call(self, req: ModelRequest) -> ModelResponse:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url=os.environ.get("DEEPSEEK_BASE_URL",
                                     "https://api.deepseek.com/v1"),
        )
        model = req.metadata.get("model") or self.default_model
        r = client.chat.completions.create(
            model=model, max_tokens=req.max_tokens,
            temperature=req.temperature,
            messages=[
                {"role": "system", "content": req.system or "You are a mesh worker."},
                {"role": "user", "content": req.prompt},
            ],
        )
        return ModelResponse(
            provider=self.name, model=model,
            text=r.choices[0].message.content or "",
            usage={"input_tokens": getattr(r.usage, "prompt_tokens", 0),
                   "output_tokens": getattr(r.usage, "completion_tokens", 0)},
        )
