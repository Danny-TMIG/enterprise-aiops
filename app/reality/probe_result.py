class RealityProbeResult(dict):
    def score(self) -> float:
        return self.get("fraction", 1.0)
