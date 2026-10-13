"""Rewrite the module-body template strings inside /tmp/parallel_train.py to
match tools/hooks/canonical_{core,mesh}.py. Idempotent, backs up first."""
import ast
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GEN = Path("/tmp/parallel_train.py")
CORE = ROOT / "tools/hooks/canonical_core.py"
MESH = ROOT / "tools/hooks/canonical_mesh.py"

if not GEN.exists():
    print(f"SKIP: {GEN} not found"); sys.exit(0)

src = GEN.read_text()
lines = src.splitlines(keepends=True)
tree = ast.parse(src)

def line_offset(lineno: int) -> int:
    return sum(len(l) for l in lines[: lineno - 1])

def find_template(*markers, min_len=800):
    """Return the largest Constant whose value contains every marker.

    Filters out small f-string fragments by size and by requiring the
    value to look like a module body (contains a triple-quote or a
    top-level `def ` / `class ` at column 0).
    """
    best = None
    for n in ast.walk(tree):
        if not isinstance(n, ast.Constant) or not isinstance(n.value, str):
            continue
        v = n.value
        if len(v) < min_len:
            continue
        if not all(m in v for m in markers):
            continue
        # module-body shape: starts with a docstring OR has a top-level def/class
        body_like = (
            v.lstrip().startswith(('"""', "'''", "#"))
            or "\ndef " in v or "\nclass " in v
            or v.startswith("def ") or v.startswith("class ")
        )
        if not body_like:
            continue
        if best is None or len(v) > len(best.value):
            best = n
    return best

def replace_value(s: str, node: ast.Constant, new_text: str) -> str:
    # span of the *raw source* including surrounding quotes
    start = line_offset(node.lineno) + node.col_offset
    end = line_offset(node.end_lineno) + node.end_col_offset
    lit = s[start:end]
    # strip prefix like r, b
    prefix = ""
    body = lit
    while body and body[0] in "rRbBuUfF":
        prefix += body[0]; body = body[1:]
    if not body or body[0] not in "\"'":
        raise ValueError(f"no quote at {start}: {lit[:20]!r}")
    q = body[0]
    # triple quote?
    if body.startswith(q * 3):
        quote = q * 3
    else:
        quote = q
    if quote in new_text:
        # canonical files use triple-double-quotes for docstrings; escape
        raise ValueError(f"canonical content contains {quote!r}; use raw string")
    return s[:start] + prefix + quote + new_text + quote + s[end:]

core_node = find_template("class Trainer", "def run_once")
mesh_node = find_template("def pollinate", "class MeshOfMeshes")

if core_node is None or mesh_node is None:
    print(f"SKIP: template lookup core={core_node is not None} mesh={mesh_node is not None}")
    sys.exit(0)

print(f"core template: {len(core_node.value)} bytes at line {core_node.lineno}")
print(f"mesh template: {len(mesh_node.value)} bytes at line {mesh_node.lineno}")

core_txt = CORE.read_text()
mesh_txt = MESH.read_text()

bak = GEN.with_suffix(f".py.bak.{int(time.time())}")
shutil.copy2(GEN, bak)
print(f"backup: {bak}")


# also fix cli.py template if present
cli_hits = find_template("for p in pl", "pollinate")
if cli_hits is not None:
    cli_txt = (ROOT / "app/train/cli.py").read_text()
    # only bake if cli.py already has the good form
    if 'p.get("stream")' in cli_txt or "p.get('stream')" in cli_txt:
        print(f"cli template: {len(cli_hits.value)} bytes at line {cli_hits.lineno}")
        # replace in the same order as the others
        if cli_hits.lineno > mesh_node.lineno:
            # re-parse after all prior replacements
            src = replace_value(src, cli_hits, cli_txt)
        else:
            src = replace_value(src, cli_hits, cli_txt)

# replace the shorter span first so offsets from the original stay valid
if mesh_node.lineno > core_node.lineno:
    src = replace_value(src, core_node, core_txt)
    # re-parse and refind mesh
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    mesh_node = find_template("def pollinate", "class MeshOfMeshes")
    src = replace_value(src, mesh_node, mesh_txt)
else:
    src = replace_value(src, mesh_node, mesh_txt)
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    core_node = find_template("class Trainer", "def run_once")
    src = replace_value(src, core_node, core_txt)

ast.parse(src)
GEN.write_text(src)
print("generator: templates baked to canonical")
