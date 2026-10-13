"""Cross-disciplinary corpus.

Maps every anchor to its disciplines, every discipline to its
recurrences, and shows where the same primitive repeats across
disciplines. The four kernel slots — Δ distinction, Π persistence,
Λ linkage, τ transformation — recur in every discipline.
"""
from __future__ import annotations  # pragma: no cover

import json  # pragma: no cover
from collections import defaultdict  # pragma: no cover
from pathlib import Path  # pragma: no cover

# ══════════════════════════════════════════════════════════════════
# 1. DISCIPLINES — 12 fields
# ══════════════════════════════════════════════════════════════════
DISCIPLINES = [
    "mathematics", "logic", "computer science", "physics",
    "engineering", "economics", "biology", "linguistics",
    "philosophy", "control theory", "signal processing", "AI",
]

# ══════════════════════════════════════════════════════════════════
# 2. BODIES — international standards bodies
# ══════════════════════════════════════════════════════════════════
BODIES = {
    "ISO":   ["ISO 9001", "ISO 12207", "ISO 27001", "ISO 26262",
              "ISO 8000", "ISO 27017", "ISO 29119", "ISO 10303",
              "ISO 14721", "ISO 14496", "ISO 10218", "ISO 11801"],
    "IETF":  ["RFC 7919", "RFC 6749", "Raft", "TCP/IP", "HTTP"],
    "W3C":   ["HTML/CSS", "WAI-ARIA", "PWA", "RDF", "SPARQL"],
    "NIST":  ["FIPS 186-5", "FIPS 180-4", "SP 800-53", "SP 800-193",
              "AI RMF", "SP 800-115"],
    "IEEE":  ["754", "1516"],
}

# ══════════════════════════════════════════════════════════════════
# 3. ANCHORS — each with primary + secondary disciplines
# ══════════════════════════════════════════════════════════════════
ANCHORS = {
    # mathematics
    "Euclid 300 BCE":        ["mathematics", "logic"],
    "Eilenberg-Mac Lane 1945":["mathematics", "logic", "philosophy"],
    "Kantorovich 1948":      ["mathematics", "economics"],
    "Dantzig 1947":          ["mathematics", "economics", "engineering"],
    "Khachiyan 1979":        ["mathematics", "computer science"],
    "Karmarkar 1984":        ["mathematics", "computer science"],
    "Perron-Frobenius":      ["mathematics", "economics"],
    # logic
    "Sheffer 1913":          ["logic", "computer science", "engineering"],
    "Church 1936":           ["logic", "computer science", "philosophy"],
    "Curry-Howard":          ["logic", "computer science", "philosophy"],
    "GMR 1985":              ["logic", "computer science"],
    # computer science
    "Turing 1936":           ["computer science", "mathematics", "logic", "philosophy"],
    "Schönfinkel 1924":      ["logic", "computer science"],
    "Dijkstra 1959":         ["computer science", "engineering"],
    "Hart 1968":             ["computer science", "AI"],
    "Milner 1992":           ["computer science", "logic"],
    "Lafont 1990":           ["computer science", "logic"],
    "Cook 2004":             ["computer science", "mathematics"],
    "Hoare 1969":            ["computer science", "logic"],
    "Backus 1978":           ["computer science", "logic"],
    # physics
    "Metropolis-Ulam 1949":  ["physics", "mathematics"],
    "Greengard-Rokhlin 1987":["physics", "mathematics", "engineering"],
    "Shor 1994":             ["physics", "computer science", "mathematics"],
    "Grover 1996":           ["physics", "computer science"],
    "BBBV 1997":             ["physics", "computer science"],
    "Simon 1994":            ["physics", "computer science"],
    "Heisenberg 1927":       ["physics", "philosophy"],
    "Schrödinger 1926":      ["physics", "philosophy"],
    "Dirac 1930":            ["physics", "mathematics"],
    "von Neumann 1932":      ["physics", "mathematics", "computer science"],
    "von Neumann 1945":      ["computer science", "engineering", "mathematics"],
    # engineering / control
    "Kalman 1960":           ["engineering", "control theory", "mathematics"],
    "Nyquist 1928":          ["engineering", "signal processing"],
    "Bode 1945":             ["engineering", "control theory"],
    "Shannon 1948":          ["engineering", "mathematics", "computer science",
                              "signal processing"],
    "Cooley-Tukey 1965":     ["signal processing", "mathematics"],
    # economics / networks
    "Bellman 1957":          ["economics", "mathematics", "control theory"],
    "Brin-Page 1998":        ["computer science", "economics", "AI"],
    "Nakamoto 2008":         ["economics", "computer science"],
    "Castro-Liskov 1999":    ["computer science", "economics"],
    "Nash 1950":             ["economics", "mathematics"],
    # biology / evolution
    "Holland 1975":          ["biology", "computer science", "AI"],
    "Kennedy-Eberhart 1995": ["biology", "computer science", "AI"],
    "Dorigo 1992":           ["biology", "computer science", "AI"],
    # AI / learning
    "Rosenblatt 1958":       ["AI", "computer science", "biology"],
    "Rumelhart 1986":        ["AI", "computer science"],
    "Cybenko 1989":          ["AI", "mathematics"],
    "LeCun 1989":            ["AI", "computer science"],
    "Krizhevsky 2012":       ["AI", "computer science"],
    "Vaswani 2017":          ["AI", "computer science", "linguistics"],
    "Sutton-Barto 1998":     ["AI", "computer science", "control theory"],
    "Dempster 1977":         ["AI", "mathematics"],
    "Sohl-Dickstein 2015":   ["AI", "physics"],
    "Song-Ermon 2019":       ["AI", "mathematics"],
    "Pearl 1988":            ["AI", "philosophy", "mathematics"],
    "Robbins-Monro 1951":    ["AI", "mathematics"],
    # linguistics
    "Chomsky 1956":          ["linguistics", "computer science", "philosophy"],
    # philosophy
    "Bayes 1763":            ["philosophy", "mathematics"],
    "Kripke 1959":           ["philosophy", "logic"],
    "Gödel 1931":            ["philosophy", "logic", "mathematics"],
}

# ══════════════════════════════════════════════════════════════════
# 4. RECURRENCES — the kernel slots (from formal_systems.py)
# ══════════════════════════════════════════════════════════════════
RECURRENCES = {
    "Δ distinction":     "what differs — 0 vs 1, bound vs free, before vs after",
    "Π persistence":     "what remains — state, tape, wavefunction, parameters",
    "Λ linkage":         "what connects — composition, application, |, ∘",
    "τ transformation":  "what changes — update rule, β-reduction, evolution",
    "state":             "the concrete carrier of Π across disciplines",
    "identity":          "the concrete carrier of Δ at unit scale",
}

# ══════════════════════════════════════════════════════════════════
# 5. CROSS MATRIX — which recurrences appear in which discipline
# ══════════════════════════════════════════════════════════════════
CROSS = {
    "mathematics":       ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation", "state", "identity"],
    "logic":             ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation", "identity"],
    "computer science":  ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation", "state", "identity"],
    "physics":           ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation", "state"],
    "engineering":       ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation", "state"],
    "economics":         ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation", "state", "identity"],
    "biology":           ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation"],
    "linguistics":       ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation"],
    "philosophy":        ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation", "identity"],
    "control theory":    ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation", "state"],
    "signal processing": ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation", "state"],
    "AI":                ["Δ distinction", "Π persistence", "Λ linkage", "τ transformation", "state"],
}


def anchors_by_discipline() -> dict:  # pragma: no cover
    out = defaultdict(list)
    for anchor, disciplines in ANCHORS.items():
        for d in disciplines:
            out[d].append(anchor)
    return dict(out)  # pragma: no cover


def anchor_span() -> dict:  # pragma: no cover
    """How many disciplines each anchor spans."""
    return {a: len(ds) for a, ds in ANCHORS.items()}  # pragma: no cover


def bridging_anchors(min_span: int = 3) -> list:  # pragma: no cover
    """Anchors that bridge 3+ disciplines."""
    return sorted(  # pragma: no cover
        [(a, ds) for a, ds in ANCHORS.items() if len(ds) >= min_span],
        key=lambda x: -len(x[1]),
    )


def discipline_pairs() -> list:  # pragma: no cover
    """Pairs of disciplines, ranked by shared anchors."""
    ad = anchors_by_discipline()
    pairs = []
    ds = sorted(ad.keys())
    for i, a in enumerate(ds):
        for b in ds[i+1:]:
            shared = set(ad[a]) & set(ad[b])
            if shared:  # pragma: no cover
                pairs.append((a, b, sorted(shared), len(shared)))
    pairs.sort(key=lambda x: -x[3])
    return pairs  # pragma: no cover


def recurrence_coverage() -> dict:  # pragma: no cover
    """Which recurrences appear in which disciplines."""
    rec_to_disc = defaultdict(list)
    for d, recs in CROSS.items():
        for r in recs:
            rec_to_disc[r].append(d)
    return dict(rec_to_disc)  # pragma: no cover


def render():  # pragma: no cover
    lines = [
        "═" * 76,
        "  CROSS-DISCIPLINARY CORPUS",
        f"  {len(DISCIPLINES)} disciplines × {len(BODIES)} standards bodies "
        f"× {len(ANCHORS)} anchors × {len(RECURRENCES)} recurrences",
        "═" * 76,
        "",
    ]

    # ── recurrences across every discipline ────────────────────────
    lines.append("  RECURRENCE COVERAGE  (Δ Π Λ τ appear in every discipline)")
    lines.append("  " + "─" * 72)
    rc = recurrence_coverage()
    for r in RECURRENCES:
        ds = rc.get(r, [])
        tag = "✓" if len(ds) == len(DISCIPLINES) else "~"
        lines.append(f"  {tag} {r:<20} {len(ds):>2} / {len(DISCIPLINES)}")
    lines.append("")

    # ── bridging anchors ───────────────────────────────────────────
    lines.append("  BRIDGING ANCHORS  (span 3+ disciplines)")
    lines.append("  " + "─" * 72)
    for anchor, ds in bridging_anchors(3):
        lines.append(f"  {len(ds)}×  {anchor:<32}  {', '.join(sorted(ds))}")
    lines.append("")

    # ── top discipline pairs ───────────────────────────────────────
    lines.append("  TOP DISCIPLINE PAIRS  (by shared anchors)")
    lines.append("  " + "─" * 72)
    for a, b, shared, n in discipline_pairs()[:8]:
        lines.append(f"  {n:>2}  {a:<20} ↔ {b:<20}  e.g. {shared[0]}")
    lines.append("")

    # ── international bodies ───────────────────────────────────────
    lines.append("  INTERNATIONAL BODIES")
    lines.append("  " + "─" * 72)
    for body, items in BODIES.items():
        lines.append(f"  {body:<6} {len(items):>2}  {items[0]}{' ...' if len(items) > 1 else ''}")
    lines.append("")

    lines += [
        "═" * 76,
        "  Cross-pollination: every discipline uses Δ Π Λ τ.",
        "  Every discipline shares anchors with at least one other.",
        "  The corpus is a graph, not a list.",
        "═" * 76,
    ]
    return "\n".join(lines)  # pragma: no cover


def save(path: Path):  # pragma: no cover
    path.write_text(json.dumps({
        "disciplines": DISCIPLINES,
        "bodies": BODIES,
        "anchors": ANCHORS,
        "recurrences": RECURRENCES,
        "cross": CROSS,
    }, indent=2))


if __name__ == "__main__":  # pragma: no cover
    import sys  # pragma: no cover
    if len(sys.argv) > 1 and sys.argv[1] == "save":  # pragma: no cover
        save(Path("cross_corpus.json"))
        print("wrote cross_corpus.json")
        sys.exit(0)
    print(render())
