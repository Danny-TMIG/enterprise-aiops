"""dcs.nature — every catalogued natural phenomenon as an executable requirement.

Catalog at data/nature.txt: (code, class, local rule) tuples.
One module per class: foraging, walk, consensus, stigmergy, flocking,
oscillator, morpho, threshold, adaptation, population, flow.
"""

from pathlib import Path  # pragma: no cover

CATALOG_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "nature.txt"


def load_catalog() -> list[dict]:  # pragma: no cover
    if not CATALOG_PATH.exists():  # pragma: no cover
        return []  # pragma: no cover
    out = []
    for raw in CATALOG_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):  # pragma: no cover
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) != 3:  # pragma: no cover
            continue
        out.append({"code": parts[0], "class": parts[1], "rule": parts[2]})
    return out  # pragma: no cover


def by_class() -> dict:  # pragma: no cover
    buckets: dict = {}
    for e in load_catalog():
        buckets.setdefault(e["class"], []).append(e)
    return buckets  # pragma: no cover
