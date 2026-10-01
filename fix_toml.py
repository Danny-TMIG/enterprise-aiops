import subprocess

print("[-] Writing clean, valid pyproject.toml...")

pyproject_content = """[build-system]
requires = ["setuptools>=61.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "enterprise_aiops"
version = "1.0.0"
description = "Enterprise AIOps local-first engine"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn>=0.28.0",
    "pydantic>=2.6.0",
    "mlx-lm>=0.19.0",
    "clickhouse-connect>=0.7.0",
    "redis>=5.0.0",
]

[project.optional-dependencies]
observability = [
    "prometheus-client>=0.19.0",
]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.2.0",
    "cyclonedx-bom>=4.0.0",
]

[tool.setuptools.packages.find]
include = ["app*", "enterprise_aiops*"]

[tool.ruff]
target-version = "py312"
line-length = 88
exclude = [
    "fix_env.py",
    "fix_pyproject.py",
    "master_verify.py",
    "bootstrap.py",
    "update_ruff_exclude.py",
    "fix_toml.py",
]

[tool.ruff.lint]
ignore = [
    "BLE001",
    "DTZ003",
    "F401",
    "F811",
    "I001",
    "UP006",
    "UP035",
]
"""

with open("pyproject.toml", "w") as f:
    f.write(pyproject_content)

print("  [+] pyproject.toml successfully reset.")
print("[-] Running 'make verify' with Python 3.12...")
subprocess.run(["make", "verify"], check=True)
