"""CMP — compiler. Expression → code object."""
import ast as _ast
from dcs.generate import requirement

def compile_expr(src: str):
    return compile(_ast.parse(src, mode="eval"), "<c>", "eval")

def eval_expr(src: str, env: dict | None = None):
    return eval(compile_expr(src), {}, env or {})

@requirement(id="DCS-CMP-001", title="expression compiler handles precedence",
             section="CMP.compiler", hats=["CMP"], criticality="MUST")
def test():
    assert eval_expr("1 + 2 * 3") == 7
    assert eval_expr("x * 2", {"x": 5}) == 10

