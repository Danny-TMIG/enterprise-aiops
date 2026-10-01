from pathlib import Path

p = Path("app/origami/grammar.py")
content = '''from typing import Any, Dict, List, Optional, Union


class Symbol:
    """Represents a grammar symbol."""
    def __init__(self, name: str, terminal: bool = False):
        self.name = name
        self.terminal = terminal

    def __repr__(self) -> str:
        return f"Symbol({self.name!r}, terminal={self.terminal})"


class Production:
    """Represents a production rule in the grammar."""
    def __init__(self, lhs: Any, rhs: List[Any], weight: float = 1.0):
        self.lhs = lhs
        self.rhs = rhs
        self.weight = weight

    def __repr__(self) -> str:
        return f"Production({self.lhs!r} -> {self.rhs!r}, weight={self.weight})"


class OrigamiGrammar:
    """Represents an Origami grammar container."""
    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.rules = rules or {}


class LoadedGrammar:
    """Represents a loaded grammar instance."""
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class WeightedGrammar:
    """Represents a weighted grammar for rule expansion and synthesis."""

    def __init__(self, rules: Optional[Dict[str, List[tuple[str, float]]]] = None):
        self.rules = rules or {}

    def add_rule(
        self, non_terminal: str, production: str, weight: float = 1.0
    ) -> None:
        if non_terminal not in self.rules:
            self.rules[non_terminal] = []
        self.rules[non_terminal].append((production, weight))


def expand(
    grammar: Union[WeightedGrammar, OrigamiGrammar, Dict[str, Any]],
    symbol: str,
    max_depth: int = 5,
) -> str:
    """Expands grammar productions starting from the given symbol."""
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
'''
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(content)
print("[✔] Successfully updated app/origami/grammar.py with all required classes.")
