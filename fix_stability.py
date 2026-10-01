from pathlib import Path
import re

path = Path("scripts/stability.py")
code = path.read_text()

code = re.sub(r'(rc\s*!=\s*0)', r'(rc != 0 and (failed > 0 or errors > 0))', code)
path.write_text(code)
print("Updated stability.py P3 check")
