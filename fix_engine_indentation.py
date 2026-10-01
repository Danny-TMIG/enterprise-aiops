import ast
import os
import re
import subprocess

os.chdir("/Users/metadusa/enterprise_aiops")

# 1. Restore pristine app/mlx_omni_engine.py from git HEAD
subprocess.run(["git", "checkout", "app/mlx_omni_engine.py"], check=True)

with open("app/mlx_omni_engine.py") as f:
    code = f.read()

# 2. Define safe, idempotent Prometheus helper functions
prometheus_helpers = """
from prometheus_client import REGISTRY, Histogram, Counter

def _get_or_create_histogram(name, documentation, labelnames=(), buckets=Histogram.DEFAULT_BUCKETS):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Histogram(name, documentation, labelnames=labelnames, buckets=buckets)

def _get_or_create_counter(name, documentation, labelnames=()):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Counter(name, documentation, labelnames=labelnames)
"""

# 3. Insert helpers right after the first import statement to ensure module-level scope
lines = code.splitlines()
insert_idx = 0
for i, line in enumerate(lines):
    if line.startswith("import ") or line.startswith("from "):
        insert_idx = i
        break

lines.insert(insert_idx, prometheus_helpers)
code = "\n".join(lines)

# 4. Replace direct metric instantiations safely across the module
code = re.sub(
    r"^\s*REQUEST_LATENCY\s*=\s*Histogram\s*\(.*?\)\s*$",
    'REQUEST_LATENCY = _get_or_create_histogram("engine_request_latency_seconds", "Request latency", ["endpoint"])',
    code,
    flags=re.MULTILINE | re.DOTALL,
)

code = re.sub(
    r"^\s*REQUEST_COUNT\s*=\s*Counter\s*\(.*?\)\s*$",
    'REQUEST_COUNT = _get_or_create_counter("engine_requests", "Engine Requests")',
    code,
    flags=re.MULTILINE | re.DOTALL,
)

# 5. Fix FastAPI response type annotations causing FastAPIError
code = re.sub(r"->\s*Response\s*\|\s*dict\b", "-> dict", code)
code = re.sub(r"->\s*dict\s*\|\s*Response\b", "-> dict", code)
code = re.sub(r"->\s*Union\[[^\]]*Response[^\]]*\]", "-> dict", code)

# 6. Validate Python syntax via AST parsing before writing
try:
    ast.parse(code)
    print("AST syntax verification passed successfully!")
except SyntaxError as e:
    print(f"SyntaxError detected: {e}")
    raise

# 7. Write out the corrected file
with open("app/mlx_omni_engine.py", "w") as f:
    f.write(code)

print("Successfully fixed app/mlx_omni_engine.py!")
