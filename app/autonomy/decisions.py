class Decision:
    def __init__(self, name: str = "", action: str = "", metadata: dict = None, **kwargs):
        self.name = name
        self.action = action
        self.metadata = metadata or {}
        for k, v in kwargs.items():
            setattr(self, k, v)

class Rule:
    def __init__(self, *args, name: str = "", condition=None, action=None, priority: int = 0, **kwargs):
        self.name = name or kwargs.get("id", "rule")
        self.condition = condition or (lambda ctx: True)
        self.action = action or (lambda ctx: None)
        self.priority = priority or kwargs.get("weight", 0)
        for k, v in kwargs.items():
            setattr(self, k, v)

class DecisionEngine:
    def __init__(self, **kwargs):
        self.rules = []
        for k, v in kwargs.items():
            setattr(self, k, v)

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def evaluate(self, context: dict):
        """First matching rule's action, or None. Backward-compatible."""
        for rule in sorted(self.rules, key=lambda r: getattr(r, "priority", 0), reverse=True):
            try:
                if callable(rule.condition) and rule.condition(context):
                    return rule.action(context) if callable(rule.action) else rule.action
            except Exception:
                continue
        return None

    def evaluate_all(self, context: dict) -> list:
        """Every matching rule's action, in priority order. Always a list."""
        out: list = []
        for rule in sorted(self.rules, key=lambda r: getattr(r, "priority", 0), reverse=True):
            try:
                if callable(rule.condition) and rule.condition(context):
                    result = rule.action(context) if callable(rule.action) else rule.action
                    if result is not None:
                        out.append(result)
            except Exception:
                continue
        return out


def evaluate_decision(
context=None):
    return DecisionEngine().evaluate_all(context or {})

