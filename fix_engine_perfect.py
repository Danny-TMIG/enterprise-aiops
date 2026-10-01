import ast
import os
import re

os.chdir("/Users/metadusa/enterprise_aiops")
path = "app/mlx_omni_engine.py"

with open(path) as f:
    code = f.read()

# 1. Clean Prometheus imports and helper block
prometheus_block = """from prometheus_client import REGISTRY, Histogram, Counter, generate_latest, CONTENT_TYPE_LATEST

def _get_or_create_histogram(name, documentation, labelnames=(), buckets=Histogram.DEFAULT_BUCKETS):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Histogram(name, documentation, labelnames=labelnames, buckets=buckets)

def _get_or_create_counter(name, documentation, labelnames=()):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Counter(name, documentation, labelnames=labelnames)
"""

# Remove old prometheus imports and helper functions if present
code = re.sub(r"from prometheus_client import.*?\n", "", code)
code = re.sub(r"def _?get_or_create_histogram.*?\n\n\n", "", code, flags=re.DOTALL)
code = re.sub(r"def _?get_or_create_histogram.*?\n\n", "", code, flags=re.DOTALL)
code = re.sub(r"def _?get_or_create_counter.*?\n\n", "", code, flags=re.DOTALL)

code = prometheus_block + "\n" + code

# 2. Fix helper function calls
code = code.replace("get_or_create_histogram(", "_get_or_create_histogram(")
code = code.replace("get_or_create_counter(", "_get_or_create_counter(")

# 3. Cleanly fix extract_document endpoint indentation and syntax
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

code = re.sub(
    r'@app\.post\("/v1/moa/extract"\)\s*async def extract_document.*?(?=\n\n\n|\n@|$)',
    extract_doc_replacement,
    code,
    flags=re.DOTALL,
)

# 4. Validate syntax with AST
try:
    ast.parse(code)
    print("AST syntax verification passed successfully!")
except SyntaxError as e:
    print(f"SyntaxError detected: {e}")
    raise

with open(path, "w") as f:
    f.write(code)

print("Successfully updated app/mlx_omni_engine.py!")
