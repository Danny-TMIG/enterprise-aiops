from typing import Any


class MoEGatingRouter:
    """Dynamic MoE Gating Network for routing document extraction tasks."""

    def __init__(self) -> None:
        self.spatial_threshold = 0.65

    def compute_gating_scores(
        self, layout_metadata: dict[str, Any]
    ) -> dict[str, float]:
        bounding_boxes = layout_metadata.get("bounding_boxes", [])
        box_density = len(bounding_boxes) / max(1, layout_metadata.get("page_count", 1))

        spatial_score = min(1.0, box_density / 50.0)
        semantic_score = 1.0 - spatial_score

        return {
            "expert_spatial_layout": spatial_score,
            "expert_semantic_extraction": semantic_score,
        }

    def route(self, layout_metadata: dict[str, Any]) -> list[str]:
        scores = self.compute_gating_scores(layout_metadata)
        sorted_experts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [expert[0] for expert in sorted_experts if expert[1] > 0.2]
