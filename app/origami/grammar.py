from typing import Any


class Symbol:
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return f"Symbol({self.name!r})"

class Production:
    def __init__(self, left: str, right: list[str]):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"Production({self.left!r} -> {self.right!r})"

class OrigamiGrammar:
    def __init__(self, rules: dict[str, list[str]] | None = None):
        self.rules = rules or {}
    def add_rule(self, lhs: str, rhs: str):
        if lhs not in self.rules:
            self.rules[lhs] = []
        self.rules[lhs].append(rhs)

class LoadedGrammar:
    def __init__(self, start_symbol: str = "S", rules=None, args=None, kwargs=None):
        self.start_symbol = start_symbol
        self.rules = rules or {}
        self.args = args or []
        self.kwargs = kwargs or {}
    def __repr__(self):
        return f"LoadedGrammar(start_symbol={self.start_symbol!r})"

class WeightedGrammar:
    def __init__(self, rules: dict[str, list[tuple[str, float]]] | None = None):
        self.rules = rules or {}
    def add_rule(self, non_terminal: str, production: str, weight: float = 1.0):
        if non_terminal not in self.rules:
            self.rules[non_terminal] = []
        self.rules[non_terminal].append((production, weight))

def _n(name: str) -> Symbol:
    return Symbol(name)

def _t(name: str) -> Symbol:
    return Symbol(name)

def expand(grammar: Any, symbol: str, max_depth: int = 5) -> str:
    if max_depth <= 0:
        return symbol
    rules = getattr(grammar, "rules", grammar)
    if symbol not in rules:
        return symbol
    productions = rules[symbol]
    if isinstance(productions, list) and len(productions) > 0:
        prod = productions[0]
        target = prod[0] if isinstance(prod, tuple) else prod
        parts = target.split()
        expanded_parts = [expand(grammar, p, max_depth - 1) for p in parts]
        return " ".join(expanded_parts)
    return symbol
