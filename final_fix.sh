#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/aether"

# 1. stop conda from hijacking PATH
conda config --set auto_activate_base false 2>/dev/null || true

# 2. ensure venv line is last in .zshrc
grep -q 'Aether: keep venv ahead' ~/.zshrc 2>/dev/null || cat >> ~/.zshrc <<'ZSH'

# Aether: keep venv ahead of conda base
if [ -d "$HOME/aether/.venv" ]; then
    export PATH="$HOME/aether/.venv/bin:$PATH"
fi
ZSH

# 3. for this shell, force the venv ahead of everything
export PATH="$HOME/aether/.venv/bin:$PATH"
hash -r

# 4. clear all bytecode and caches
find . -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
rm -rf .pytest_cache

# 5. remove the xfail block from test_imports.py
python3 - <<'PYEOF'
import pathlib
p = pathlib.Path("tests/test_imports.py")
s = p.read_text()
old = '''    # One known phantom — recorded, not silenced
    known_phantom = [
        f for f in failures
        if f.startswith("GOV-FED-001") and "src.public.gateway" in f
    ]
    unexpected = [f for f in failures if f not in known_phantom]

    if known_phantom:
        pytest.xfail(
            f"known phantom import on GOV-FED-001: {known_phantom[0]}"
        )

    assert not unexpected, (
        f"{len(unexpected)} unexpected import failures:\\n"
        + "\\n".join(unexpected[:10])
    )'''
new = '''    assert not failures, (
        f"{len(failures)} import failures:\\n"
        + "\\n".join(failures[:10])
    )'''
if old in s:
    p.write_text(s.replace(old, new))
    print("removed xfail block")
else:
    print("xfail block not found — file already clean")
PYEOF

# 6. verify
echo "--- which python ---"
which python
python --version

echo "--- pytest ---"
python -m pytest -q 2>&1 | tail -8

# 7. commit and push
echo "--- committing ---"
git add tests/ pytest.ini .coveragerc tooling/validation/status.py 2>/dev/null || true
git add -A
git commit -s -m "test: complete top-level ASF suite, conda PATH fix, remove xfail" || echo "nothing to commit"
git push origin main

echo
echo "===================== DONE ====================="
echo "open a NEW terminal window for the PATH change to stick"
echo "then: cd ~/aether && python -m pytest -q"
