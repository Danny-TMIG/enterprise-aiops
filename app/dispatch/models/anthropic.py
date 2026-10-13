from __future__ import annotations

import os

from app.dispatch.models.base import ModelProvider, ModelRequest, ModelResponse


class AnthropicProvider(ModelProvider):
    name = "anthropic"
    default_model = "claude-sonnet-4-6"

    def available(self) -> bool:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return False
        try:
            import anthropic  # noqa: F401
            return True
        except Exception:
            return False

    def _call(self, req: ModelRequest) -> ModelResponse:
        import anthropic
        client = anthropic.Anthropic()
        model = req.metadata.get("model") or self.default_model
        msg = client.messages.create(
            model=model,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            system=req.system or "You are a mesh worker.",
            messages=[{"role": "user", "content": req.prompt}],
        )
        text = "".join(
            b.text for b in msg.content if getattr(b, "type", "") == "text"
        )
        return ModelResponse(
            provider=self.name, model=model, text=text,
            usage={"input_tokens": msg.usage.input_tokens,
                   "output_tokens": msg.usage.output_tokens},
        )
