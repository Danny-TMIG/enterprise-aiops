#!/usr/bin/env python3
import re
from pathlib import Path

UNGUARDED_FILES = [
    Path("app/botnetmastery/cli.py"),
    Path("app/agency/cli.py"),
    Path("app/atlas/moats_cli.py"),
    Path("app/atlas/cli.py")
]

def guard_module_parsers():
    for path in UNGUARDED_FILES:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        if "if __name__ ==" in content:
            continue
            
        print(f"Guarding parser execution in {path}")
        
        # Simple heuristic: wrap file content or append main guard if parse_args is top-level
        lines = content.splitlines()
        new_lines = []
        in_main_block = False
        
        for line in lines:
            if re.match(r"^\s*[\w\.]*parse_args\(", line):
                new_lines.append(f"    {line.strip()}")
            else:
                new_lines.append(line)
                
        # If no explicit main function exists, wrap execution logic
        wrapped_content = "\n".join(new_lines)
        if "def main(" not in wrapped_content:
            wrapped_content += "\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()\n"
        else:
            if "if __name__ == '__main__':" not in wrapped_content:
                wrapped_content += "\n\nif __name__ == '__main__':\n    main()\n"
                
        path.write_text(wrapped_content, encoding="utf-8")

def run_fix():
    print("Applying test suite isolation and module guards...")
    
    conftest_path = Path("conftest.py")
    fixture_code = '''
import sys
import pytest

@pytest.fixture(autouse=True)
def _isolate_cli_args(monkeypatch):
    monkeypatch.setattr(sys, "argv", [sys.argv[0]])
'''.strip()

    if conftest_path.exists():
        conftest_content = conftest_path.read_text(encoding="utf-8")
        if "_isolate_cli_args" not in conftest_content:
            conftest_path.write_text(conftest_content + "\n\n" + fixture_code + "\n", encoding="utf-8")
    else:
            conftest_path.write_text(fixture_code + "\n", encoding="utf-8")

    guard_module_parsers()
    print("Fixes applied successfully. Run pytest now.")

if __name__ == "__main__":
    run_fix()
