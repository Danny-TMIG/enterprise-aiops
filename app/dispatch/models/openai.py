from __future__ import annotations

import os

from app.dispatch.models.base import ModelProvider, ModelRequest, ModelResponse


class OpenAIProvider(ModelProvider):
    name = "openai"
    default_model = "gpt-5"

    def available(self) -> bool:
        if not os.environ.get("OPENAI_API_KEY"):
            return False
        try:
            import openai  # noqa: F401
            return True
        except Exception:
            return False

    def _call(self, req: ModelRequest) -> ModelResponse:
        from openai import OpenAI
        client = OpenAI()
        model = req.metadata.get("model") or self.default_model
        r = client.chat.completions.create(
            model=model,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            messages=[
                {"role": "system", "content": req.system or "You are a mesh worker."},
                {"role": "user", "content": req.prompt},
            ],
        )
        text = r.choices[0].message.content or ""
        usage = getattr(r, "usage", None)
        return ModelResponse(
            provider=self.name, model=model, text=text,
            usage={
                "input_tokens": getattr(usage, "prompt_tokens", 0),
                "output_tokens": getattr(usage, "completion_tokens", 0),
            },
        )
