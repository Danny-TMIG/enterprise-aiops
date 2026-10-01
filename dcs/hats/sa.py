"""SA — solutions arch. Architecture graph is a DAG."""
from dcs.generate import requirement

def is_dag(nodes: dict[str, list[str]]) -> bool:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in nodes}
    def visit(n):
        color[n] = GRAY
        for m in nodes.get(n, []):
            if color.get(m, WHITE) == GRAY: return False
            if color.get(m, WHITE) == WHITE and not visit(m): return False
        color[n] = BLACK
        return True
    return all(visit(n) for n in nodes if color[n] == WHITE)

@requirement(id="DCS-SA-001", title="arch graph is acyclic",
             section="SA.solutionsarch", hats=["SA"], criticality="MUST")
def test():
    assert is_dag({"ui": ["api"], "api": ["db"], "db": []})
    assert not is_dag({"a": ["b"], "b": ["a"]})

