import ast
import re
import subprocess

# 1. Clean up any leftover temp scripts
for filename in [
    "fix_tests.py",
    "fix_engine.py",
    "clean_engine.py",
    "reset_and_fix_engine.py",
    "fix_engine_clean.py",
    "fix_properly.py",
]:
    subprocess.run(["rm", "-f", filename], check=False)

# 2. Checkout clean mlx_omni_engine.py from git
subprocess.run(["git", "checkout", "app/mlx_omni_engine.py"], check=True)

with open("app/mlx_omni_engine.py") as f:
    code = f.read()

# 3. Fix FastAPI Response | dict or similar type annotations causing FastAPIError
code = re.sub(r"->\s*Response\s*\|\s*dict\b", "-> dict", code)
code = re.sub(r"->\s*dict\s*\|\s*Response\b", "-> dict", code)
code = re.sub(r"->\s*Union\[[^\]]*Response[^\]]*\]", "-> dict", code)

# 4. Add idempotent Prometheus metric helpers at the top
prometheus_helpers = """from prometheus_client import REGISTRY, Histogram, Counter

def _get_or_create_histogram(name, documentation, labelnames=(), buckets=Histogram.DEFAULT_BUCKETS):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Histogram(name, documentation, labelnames=labelnames, buckets=buckets)

def _get_or_create_counter(name, documentation, labelnames=()):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Counter(name, documentation, labelnames=labelnames)
"""

code = prometheus_helpers + "\n" + code

# 5. Replace metric instantiations
code = re.sub(
    r"REQUEST_LATENCY\s*=\s*Histogram\s*\([^)]*\)",
    'REQUEST_LATENCY = _get_or_create_histogram("engine_request_latency_seconds", "Request latency", ["endpoint"])',
    code,
)

code = re.sub(
    r"REQUEST_COUNT\s*=\s*Counter\s*\([^)]*\)",
    'REQUEST_COUNT = _get_or_create_counter("engine_requests", "Engine Requests")',
    code,
)

# 6. Validate Python syntax
ast.parse(code)

with open("app/mlx_omni_engine.py", "w") as f:
    f.write(code)

print("Applied fix successfully.")
