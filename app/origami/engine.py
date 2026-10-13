from typing import Any


class OrigamiEngine:
    def __init__(self, layers: int = 3):
        self.layers = layers
        self.folded_state = [f"layer-{i}" for i in range(layers)]

    def fold(self, transformation: str) -> list[str]:
        self.folded_state.append(transformation)
        return self.folded_state

    def unfold(self) -> list[str]:
        if self.folded_state:
            self.folded_state.pop()
        return self.folded_state

    def inspect(self) -> dict[str, Any]:
        return {
            "layers": self.layers,
            "state_count": len(self.folded_state),
            "folded_state": self.folded_state
        }
