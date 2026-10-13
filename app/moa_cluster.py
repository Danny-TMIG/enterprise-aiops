import asyncio
from typing import Any

try:
    from mlx_lm import *  # type: ignore
    _MLX_LM_OK = True
except Exception:
    _MLX_LM_OK = False

from app.moe_router import MoEGatingRouter


class MLXWorkerNode:
    def __init__(self, node_id: str, model_path: str, specialization: str) -> None:
        self.node_id = node_id
        self.model_path = model_path
        self.specialization = specialization
        print(f"[Worker {self.node_id}] Loading weights from {self.model_path}...")
        self.model, self.tokenizer = load(self.model_path)  # type: ignore[misc]
        print(f"[Worker {self.node_id}] Ready. Specialization: {self.specialization}")

    async def execute(self, prompt: str, context: dict[str, Any] | None = None) -> str:
        loop = asyncio.get_running_loop()
        formatted_prompt = (
            f"[Role: {self.specialization}]\nContext: {context}\nTask: {prompt}"
        )
        response = await loop.run_in_executor(
            None,
            lambda: generate(
                self.model,
                self.tokenizer,
                prompt=formatted_prompt,
                verbose=False,
                max_tokens=512,
            ),
        )
        return response.strip()


class MoAOrchestrator:
    def __init__(self) -> None:
        self.router = MoEGatingRouter()
        self.experts = {
            "expert_spatial_layout": MLXWorkerNode(
                node_id="worker_spatial",
                model_path="mlx-community/Qwen2.5-7B-Instruct-4bit",
                specialization="LayoutLM Bounding Box & Spatial Parser",
            ),
            "expert_semantic_extraction": MLXWorkerNode(
                node_id="worker_semantic",
                model_path="mlx-community/Qwen2.5-7B-Instruct-4bit",
                specialization="Key-Value Entity Normalization & Slot Filling",
            ),
        }
        self.aggregator = MLXWorkerNode(
            node_id="aggregator_node",
            model_path="mlx-community/Qwen2.5-7B-Instruct-4bit",
            specialization="Cross-Agent Critique and Final Structured JSON Synthesis",
        )

    async def process_request(
        self, document_text: str, layout_metadata: dict[str, Any]
    ) -> str:
        selected_experts = self.router.route(layout_metadata)

        worker_tasks = [
            self.experts[expert_name].execute(
                prompt=document_text, context=layout_metadata
            )
            for expert_name in selected_experts
            if expert_name in self.experts
        ]
        worker_outputs = await asyncio.gather(*worker_tasks)

        synthesis_context = {
            f"agent_{i}_output": out for i, out in enumerate(worker_outputs)
        }
        aggregator_prompt = "Synthesize extractions into a single verified JSON document, resolving spatial conflicts."

        return await self.aggregator.execute(
            prompt=aggregator_prompt, context=synthesis_context
        )
