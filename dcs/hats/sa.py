"""SA — solutions arch. Architecture graph is a DAG."""

from dcs.generate import requirement  # pragma: no cover


def is_dag(nodes: dict[str, list[str]]) -> bool:  # pragma: no cover
    WHITE, GRAY, BLACK = 0, 1, 2
    color = dict.fromkeys(nodes, WHITE)

    def visit(n):  # pragma: no cover
        color[n] = GRAY
        for m in nodes.get(n, []):
            if color.get(m, WHITE) == GRAY:  # pragma: no cover
                return False  # pragma: no cover
            if color.get(m, WHITE) == WHITE and not visit(m):  # pragma: no cover
                return False  # pragma: no cover
        color[n] = BLACK
        return True  # pragma: no cover

    return all(visit(n) for n in nodes if color[n] == WHITE)  # pragma: no cover


@requirement(
    id="DCS-SA-001",
    title="arch graph is acyclic",
    section="SA.solutionsarch",
    hats=["SA"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert is_dag({"ui": ["api"], "api": ["db"], "db": []})
    assert not is_dag({"a": ["b"], "b": ["a"]})
