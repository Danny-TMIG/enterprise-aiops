"""Grammar atlas — taxonomy + guaranteed 4-letter pool."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

CATEGORIES = (
    "Phonology", "Morphology", "Syntax",
    "Semantics", "Pragmatics", "Discourse", "Theoretical grammar",
)

_FALLBACK_4 = [
    "tone", "stop", "vowel", "nasal", "glide",
    "root", "stem", "affix", "word", "form", "case",
    "noun", "verb", "head", "node", "tree",
    "type", "sort", "term", "role", "mode",
    "face", "turn", "self", "act", "text",
    "genre", "frame", "topic", "comment",
    "merge", "move", "feature",
]


@dataclass
class Atlas:
    categories: dict[str, list[str]]
    name: str = "default"

    def __post_init__(self):
        for c in CATEGORIES:
            self.categories.setdefault(c, [])
        # guarantee a 4-letter pool of >= 4 distinct words
        have = set(self.by_length(4))
        for w in _FALLBACK_4:
            if w not in have:
                # put it in the first category
                self.categories[CATEGORIES[0]].append(w)
                have.add(w)

    def by_category(self, c):
        return list(self.categories.get(c, []))

    def by_length(self, n):
        out = []
        for terms in self.categories.values():
            for t in terms:
                if len(t) == n:
                    out.append(t)
        return sorted(set(out))

    def categories_for_length(self, n):
        out = {}
        for c, terms in self.categories.items():
            hit = [t for t in terms if len(t) == n]
            if hit:
                out[c] = hit
        return out

    def to_dict(self):
        return {"name": self.name,
                "counts": {k: len(v) for k, v in self.categories.items()}}


def load_atlas(path=None, name="default"):
    if path is not None and Path(path).exists():
        data = json.loads(Path(path).read_text())
        cats = data.get("Grammar", data)
        return Atlas(categories=cats, name=str(path))
    default_path = Path(__file__).resolve().parent.parent / "grammar" / "taxonomy.json"
    if default_path.exists():
        data = json.loads(default_path.read_text())
        cats = data.get("Grammar", data)
        return Atlas(categories=cats, name=str(default_path.name))
    return Atlas(categories={c: [] for c in CATEGORIES}, name=name)
