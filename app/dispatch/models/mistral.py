from __future__ import annotations

import os

from app.dispatch.models.base import ModelProvider, ModelRequest, ModelResponse


class MistralProvider(ModelProvider):
    name = "mistral"
    default_model = "mistral-large-latest"

    def available(self) -> bool:
        if not os.environ.get("MISTRAL_API_KEY"):
            return False
        try:
            import mistralai  # noqa: F401
            return True
        except Exception:
            return False

    def _call(self, req: ModelRequest) -> ModelResponse:
        from mistralai import Mistral
        client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
        model = req.metadata.get("model") or self.default_model
        r = client.chat.complete(
            model=model,
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
