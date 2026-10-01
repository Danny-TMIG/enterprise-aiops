import ast
import os
import re

os.chdir("/Users/metadusa/enterprise_aiops")
path = "app/mlx_omni_engine.py"

with open(path) as f:
    code = f.read()

# 1. Ensure safe Prometheus helper functions are present at module level
if "_get_or_create_histogram" not in code:
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
    lines = code.splitlines()
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_idx = i
            break
    lines.insert(insert_idx, prometheus_helpers)
    code = "\n".join(lines)

# 2. Replace direct metric instantiations safely
code = re.sub(
    r"REQUEST_LATENCY\s*=\s*Histogram\s*\(.*?\)",
    'REQUEST_LATENCY = _get_or_create_histogram("engine_request_latency_seconds", "Request latency", ["endpoint"])',
    code,
    flags=re.DOTALL,
)
code = re.sub(
    r"REQUEST_COUNT\s*=\s*Counter\s*\(.*?\)",
    'REQUEST_COUNT = _get_or_create_counter("engine_requests", "Engine Requests")',
    code,
    flags=re.DOTALL,
)

# 3. Fix FastAPI response type annotations
code = re.sub(r"->\s*Response\s*\|\s*dict\b", "-> dict", code)
code = re.sub(r"->\s*dict\s*\|\s*Response\b", "-> dict", code)
code = re.sub(r"->\s*Union\[[^\]]*Response[^\]]*\]", "-> dict", code)

# 4. Cleanly replace the extract_document function to guarantee correct indentation and syntax
extract_doc_replacement = """@app.post("/v1/moa/extract")
async def extract_document(req: DocumentRequest) -> dict:
    try:
        result = await orchestrator.process_request(
            document_text=req.document_text,
            layout_metadata=req.layout_metadata,
        )
        return {"status": "success", "extracted_payload": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""

# Replace whatever extract_document currently looks like with the correctly indented version
code = re.sub(
    r'@app\.post\("/v1/moa/extract"\)\s*async def extract_document.*?(?=\n\n|\n@|$)',
    extract_doc_replacement,
    code,
    flags=re.DOTALL,
)

# 5. Validate syntax with AST
try:
    ast.parse(code)
    print("AST syntax verification passed!")
except SyntaxError as e:
    print(f"SyntaxError remaining: {e}")
    raise

# 6. Write back to file
with open(path, "w") as f:
    f.write(code)

print("Successfully fixed app/mlx_omni_engine.py!")
