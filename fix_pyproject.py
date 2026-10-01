import subprocess

print("[-] Fixing pyproject.toml package discovery and build-system...")

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

print("  [+] pyproject.toml updated successfully.")

# Run pip install again inside the Python 3.12 venv
pip_bin = ".venv/bin/pip"
print("[-] Installing package in editable mode with Python 3.12...")
subprocess.run([pip_bin, "install", "-e", ".[observability,dev]"], check=True)

print("\n🎉 Environment fixed and dependencies installed successfully!")
print("[-] Running 'make verify'...")
subprocess.run(["make", "verify"], check=True)
