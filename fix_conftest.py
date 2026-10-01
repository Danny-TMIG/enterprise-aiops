from pathlib import Path

def clean_conftests():
    fixture_code = '''import sys
import pytest

@pytest.fixture(autouse=True)
def _isolate_cli_args(monkeypatch):
    monkeypatch.setattr(sys, "argv", [sys.argv[0]])
'''.strip()

    for path in [Path("conftest.py"), Path("tests/conftest.py")]:
        if path.parent.exists():
            # Read existing if any, remove duplicate/broken fixture code
            content = path.read_text(encoding="utf-8") if path.exists() else ""
            if "_isolate_cli_args" not in content:
                new_content = content.rstrip() + "\n\n" + fixture_code + "\n"
                path.write_text(new_content, encoding="utf-8")
                print(f"Updated {path}")
            else:
                print(f"Fixture already in {path}")

if __name__ == "__main__":
    clean_conftests()
