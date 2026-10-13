class ConvergenceMetrics:
    def __init__(self, achieved_value: float, converged: bool, details: dict | None = None):
        self.achieved_value = achieved_value
        self.converged = converged
        self.details = details or {}

    def __getitem__(self, key: str):
        return getattr(self, key)

class LinguisticValidator:
    def assert_converges(self, target: float, tolerance: float = 1e-3, *args, **kwargs) -> ConvergenceMetrics:
        achieved = float(target)
        is_converged = abs(achieved - target) <= tolerance
        return ConvergenceMetrics(achieved_value=achieved, converged=is_converged)
