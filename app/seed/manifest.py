from dataclasses import dataclass


class Manifest:
    def __init__(self, version: str = "1.0", **kwargs):
        self.version = version
        for k, v in kwargs.items():
            setattr(self, k, v)

def load_manifest() -> Manifest:
    return Manifest(version="1.0")


@dataclass
class CPVORates:
    """Cost per value unit. rate * value == cpvo_usd."""
    rate: float = 1.0

    def apply(self, value: float) -> float:
        return value * self.rate
