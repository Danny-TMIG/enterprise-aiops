import ast
import os
import re

os.chdir("/Users/metadusa/enterprise_aiops")
path = "app/mlx_omni_engine.py"

with open(path) as f:
    code = f.read()

# 1. Clean up old prometheus imports and helper functions
code = re.sub(r"from prometheus_client import.*?\n", "", code)
code = re.sub(
    r"def _?get_or_create_histogram.*?\n\s*return.*?\n", "", code, flags=re.DOTALL
)
code = re.sub(
    r"def _?get_or_create_counter.*?\n\s*return.*?\n", "", code, flags=re.DOTALL
)

# 2. Insert correct imports and robust helper functions at the top
prometheus_block = """from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, Counter, Histogram, generate_latest

def _get_or_create_histogram(name, documentation, labelnames=(), buckets=Histogram.DEFAULT_BUCKETS):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Histogram(name, documentation, labelnames=labelnames, buckets=buckets)

def _get_or_create_counter(name, documentation, labelnames=()):
    if name in REGISTRY._names_to_collectors:
        return REGISTRY._names_to_collectors[name]
    return Counter(name, documentation, labelnames=labelnames)
"""

code = prometheus_block + "\n" + code

# 3. Ensure all metric instantiations use the underscored helpers
code = code.replace("get_or_create_histogram(", "_get_or_create_histogram(")
code = code.replace("get_or_create_counter(", "_get_or_create_counter(")

# 4. Properly format and indent the /v1/moa/extract endpoint
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

# 5. Validate AST syntax before writing
try:
    ast.parse(code)
    print("AST syntax verification passed successfully!")
except SyntaxError as e:
    print(f"SyntaxError detected: {e}")
    raise

with open(path, "w") as f:
    f.write(code)

print("Successfully updated app/mlx_omni_engine.py!")
