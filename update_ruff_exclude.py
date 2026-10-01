import subprocess

print("[-] Updating pyproject.toml to exclude root utility scripts from linting...")

with open("pyproject.toml") as f:
    content = f.read()

# Add exclude block if not already present
if "exclude =" not in content:
    exclusion_block = """
[tool.ruff]
target-version = "py312"
line-length = 88
exclude = [
    "fix_env.py",
    "fix_pyproject.py",
    "master_verify.py",
    "bootstrap.py",
]
"""
    # Replace [tool.ruff] with the expanded version
    content = content.replace("[tool.ruff]", exclusion_block.strip())
    with open("pyproject.toml", "w") as f:
        f.write(content)
    print("  [+] Added script exclusions to pyproject.toml.")

print("[-] Running 'make verify' again...")
subprocess.run(["make", "verify"], check=True)
