from pathlib import Path

p = Path("app/origami/grammar.py")
if p.exists():
    content = p.read_text()
    if "LoadedGrammar" not in content:
        content += "\n\nclass LoadedGrammar:\n    def __init__(self, *args, **kwargs):\n        pass\n"
        p.write_text(content)
        print("[✔] Added LoadedGrammar stub to app/origami/grammar.py")
else:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("class LoadedGrammar:\n    def __init__(self, *args, **kwargs):\n        pass\n")
    print("[✔] Created app/origami/grammar.py with LoadedGrammar stub")
