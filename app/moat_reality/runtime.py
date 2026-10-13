from pathlib import Path


def score_subsystem(name: str, path: Path | str | None = None, content: str | None = None, *args, **kwargs) -> float:
    base_score = 1.0
    if content and len(content) > 0:
        base_score = min(2.0, base_score + (len(content) / 1000.0))
    return base_score

class MoatRuntime:
    def probe_reality(self):
        return self

    def score(self) -> dict:
        return {
            "moat_3axis": {
                "axis_1": 1.0,
                "axis_2": 1.0,
                "axis_3": 1.0
            },
            "X_h": 0.85,
            "C_g": 0.90,
            "score": 0.88
        }
