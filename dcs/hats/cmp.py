"""CMP — compiler. Expression → code object."""

import ast as _ast  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def compile_expr(src: str):  # pragma: no cover
    return compile(_ast.parse(src, mode="eval"), "<c>", "eval")  # pragma: no cover


def eval_expr(src: str, env: dict | None = None):  # pragma: no cover
    return eval(compile_expr(src), {}, env or {})  # pragma: no cover


@requirement(
    id="DCS-CMP-001",
    title="expression compiler handles precedence",
    section="CMP.compiler",
    hats=["CMP"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert eval_expr("1 + 2 * 3") == 7
    assert eval_expr("x * 2", {"x": 5}) == 10
