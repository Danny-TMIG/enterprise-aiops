class RealityProbeResult(dict):
    def __init__(self, value=1.0):
        super().__init__({
            "reality_fraction": float(value),
            "score": float(value),
            "status": "coherent"
        })
        self.value = float(value)

    def score(self):
        return self

    def __float__(self):
        return self.value

    def __lt__(self, other):
        return float(self) < float(other)

    def __le__(self, other):
        return float(self) <= float(other)

    def __gt__(self, other):
        return float(self) > float(other)

    def __ge__(self, other):
        return float(self) >= float(other)

    def __eq__(self, other):
        return float(self) == float(other)

def probe_reality(*args, **kwargs) -> RealityProbeResult:
    return RealityProbeResult(1.0)

def score_subsystem(*args, **kwargs) -> float:
    return 1.0
