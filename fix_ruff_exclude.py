import subprocess

print("[-] Updating pyproject.toml to exclude .venv from Ruff linting...")

with open("pyproject.toml") as f:
    content = f.read()

# Replace or add exclude rule for .venv
if "exclude =" in content:
    content = content.replace("exclude = [", 'exclude = [\n    ".venv",')
else:
    content += """
[tool.ruff]
exclude = [".venv"]
"""

with open("pyproject.toml", "w") as f:
    f.write(content)

print("[-] Running 'make verify'...")
subprocess.run(["make", "verify"], check=True)
