"""Ten moats — unique core algorithms / architectures.

Each moat is a defensible capability. Every moat names:
    id            1..10
    name          short name
    description   what it is
    value         the moat class (patent / trade-secret / network /
                  compliance / performance)
    implementers  modules in this repo that realize it, if any
    residuals     residual IDs from app.residual.register
    status        "shipped" | "partial" | "planned"

This is a live registry. The markdown projection is generated
from the data here by `write_markdown()`.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Moat:
    id: int
    name: str
    description: str
    value: str
    implementers: tuple[str, ...]
    residuals: tuple[str, ...]
    status: str

    def to_dict(self) -> dict:
        return asdict(self)


_MOATS: tuple[Moat, ...] = (
    Moat(
        id=1,
        name="Braided multimodal fusion engine",
        description=(
            "Deterministically fuses vision/audio/text/quantum outputs "
            "into a single latent for reasoning. Novel fusion rules, "
            "gating, and attention sparsity patterns. The braid is the "
            "operational semantics: interleaved channels that commute "
            "under a fixed crossing invariant."
        ),
        value="patent (novel fusion rules)",
        implementers=(
            "app.combinator (braid as graph reduction)",
            "app.math.graph (fusion topology)",
            "app.nested (multi-level fusion)",
        ),
        residuals=("K-27", "M-23", "Z-12"),
        status="partial",
    ),
    Moat(
        id=2,
        name="Self-healing orchestration with causal tracing",
        description=(
            "Intent-aware restart and placement decisions driven by "
            "causal traces, not liveness checks. Tie into cost, energy, "
            "and latency models. Restart a node only when the causal "
            "chain that failed is understood; otherwise escalate."
        ),
        value="patent + operations",
        implementers=(
            "app.autonomy.healer",
            "app.autonomy.watchdog",
            "app.meta.loop",
            "app.moat.axes",
        ),
        residuals=("X-01", "X-04", "X-08", "T-25"),
        status="partial",
    ),
    Moat(
        id=3,
        name="Proprietary datasets and curation pipeline",
        description=(
            "High-quality domain-specific datasets: curated, deduplicated, "
            "fingerprinted. Automated lineage, provenance, labeling. "
            "Synthetic augmentation to extend real data safely."
        ),
        value="trade-secret",
        implementers=(
            "app.delta.corpus (BM25 retrieval)",
            "app.delta.curriculum (SFT/DPO emission)",
            "app.backrooms (residue store)",
        ),
        residuals=("I-02", "M-18", "S-11"),
        status="partial",
    ),
    Moat(
        id=4,
        name="Fine-tuning + quantization for local hardware",
        description=(
            "Automated quantization / pruning producing small accurate "
            "models for WebGPU / Apple Silicon / CPU. Guaranteed "
            "latency-accuracy tradeoffs. Reproducible deterministic builds."
        ),
        value="performance + product differentiation",
        implementers=(
            "app.dispatch.models.local_mlx",
            "app.origami.library (grammar compilation)",
            "app.reality (environment reproducibility)",
        ),
        residuals=("P-14", "I-02", "T-19"),
        status="partial",
    ),
    Moat(
        id=5,
        name="Reproducible auditable build + signed SBOMs",
        description=(
            "Deterministic stage-0 to stage-N builds. Content-addressed "
            "artifacts. SBOMs. Cryptographic signing. Supply-chain "
            "attestations (in-toto)."
        ),
        value="compliance + enterprise trust",
        implementers=(
            "app.seed.manifest",
            "app.seed.seal",
            "app.proof.regulatory",
            "app.reality.install",
        ),
        residuals=("T-21", "T-28", "T-29", "K-15"),
        status="partial",
    ),
    Moat(
        id=6,
        name="Policy-driven safety + compliance platform",
        description=(
            "Policy DSL tailored to AI behaviours: data access, "
            "hallucination gates, decision logging. Automatic policy "
            "drift detection. Audit reports."
        ),
        value="regulatory readiness",
        implementers=(
            "app.moat.runtime",
            "app.meta.observer",
            "app.federation.privacy",
            "app.canon.commandments",
        ),
        residuals=("G-13", "T-31", "T-32"),
        status="partial",
    ),
    Moat(
        id=7,
        name="Novel UI/UX and developer platform (SDK + API)",
        description=(
            "Multi-language SDKs. Reproducible local sandboxes. "
            "One-click orchestration CLI. Turn runtime capabilities "
            "into platform lock-in."
        ),
        value="network effect + licensing",
        implementers=(
            "app.reconfig (intent → code)",
            "app.engines (parallel grid runner)",
            "app.train (curriculum + metrics)",
        ),
        residuals=("T-24", "D-15", "G-01"),
        status="partial",
    ),
    Moat(
        id=8,
        name="Hybrid trust: federated + local with DP",
        description=(
            "Federated learning orchestration keeping data local, "
            "aggregating updates securely. Differential privacy for "
            "safe model updates."
        ),
        value="privacy-first customers",
        implementers=(
            "app.federation.consensus",
            "app.federation.privacy",
            "app.federation.provenance",
            "app.federation.security",
        ),
        residuals=("D-01", "D-02", "G-09", "S-06"),
        status="partial",
    ),
    Moat(
        id=9,
        name="Hardware kernels: M-series, AVX, CUDA, WebGPU",
        description=(
            "Hand-tuned kernels for Apple M-series, AVX2/AVX512, CUDA, "
            "and WebGPU shaders for common ops. Performance claims "
            "backed by reproducible benchmarks."
        ),
        value="performance + patent",
        implementers=(
            "app.math (numerical primitives)",
            "app.ddlong.dd (double-double arithmetic)",
            "app.substrate (RAM / streaming)",
        ),
        residuals=("C-22", "P-14", "H-14"),
        status="planned",
    ),
    Moat(
        id=10,
        name="Orchestration semantics / declarative braid language",
        description=(
            "Compact declarative language for braid workflows: data "
            "pipelines + model orchestration + policies + cost "
            "constraints. Compiles to runtime. Language IP is a "
            "high-value product."
        ),
        value="platform lock-in + patent",
        implementers=(
            "app.reconfig.rules (rule language)",
            "app.reconfig.codeal (Code-AL IR)",
            "app.chain (36-role composition)",
            "app.cst (predicate loop)",
        ),
        residuals=("K-27", "C-19", "T-11"),
        status="partial",
    ),
    Moat(
        id=11,
        name="Ecosystem: reference apps, templates, marketplace",
        description=(
            "Reference applications, case studies, paid templates, "
            "partner integrations. Signing and trust marketplace for "
            "models."
        ),
        value="revenue + adoption",
        implementers=(
            "app.proprietary (registry of vendor integrations)",
            "app.frontier (research profiles)",
            "app.puzzles + app.engines + app.train (demonstrators)",
            "app.canon (governance docs)",
        ),
        residuals=("G-01", "N-06", "N-16"),
        status="partial",
    ),
)


# ── queries ─────────────────────────────────────────────────────
def by_status(status: str) -> list[Moat]:
    return [m for m in _MOATS if m.status == status]


def by_implementer(module_substr: str) -> list[Moat]:
    s = module_substr.lower()
    out: list[Moat] = []
    for m in _MOATS:
        for impl in m.implementers:
            if s in impl.lower():
                out.append(m)
                break
    return out


def by_residual(rid: str) -> list[Moat]:
    return [m for m in _MOATS if rid in m.residuals]


def search(substr: str) -> list[Moat]:
    s = substr.lower()
    return [m for m in _MOATS
            if s in m.name.lower()
            or s in m.description.lower()
            or s in m.value.lower()]


def all_moats() -> tuple[Moat, ...]:
    return _MOATS


# ── validation ──────────────────────────────────────────────────
def validate() -> dict:
    try:
        from app.residual import register as R
    except Exception as e:
        return {"ok": False, "reason": f"register not importable: {e}"}

    bad: dict[int, list[str]] = {}
    for m in _MOATS:
        for rid in m.residuals:
            if not R.is_valid(rid):
                bad.setdefault(m.id, []).append(rid)

    ids = [m.id for m in _MOATS]
    statuses = sorted(set(m.status for m in _MOATS))
    return {
        "ok": not bad and ids == list(range(1, len(_MOATS) + 1)),
        "count": len(_MOATS),
        "ids_contiguous": ids == list(range(1, len(_MOATS) + 1)),
        "statuses_present": statuses,
        "invalid_residuals": bad,
    }


# ── markdown projection ────────────────────────────────────────
def render_markdown() -> str:
    out: list[str] = []
    out.append("# Ten Moats — Unique Core Algorithms / Architectures")
    out.append("")
    out.append("A live registry. The doc is a projection of")
    out.append("`app/atlas/moats.py`. Edit the data in that module and")
    out.append("re-run `python3 -m app.atlas.moats_cli --write` to regenerate.")
    out.append("")
    out.append(f"Total moats: **{len(_MOATS)}**.")
    out.append("")
    out.append("| # | Moat | Value class | Status | Implementers | Residuals |")
    out.append("|---|------|-------------|--------|--------------|-----------|")
    for m in _MOATS:
        impl = ", ".join(f"`{i.split(' ')[0]}`" for i in m.implementers)
        res = ", ".join(f"`{r}`" for r in m.residuals)
        out.append(f"| {m.id} | {m.name} | {m.value} | {m.status} | "
                   f"{impl} | {res} |")
    out.append("")

    out.append("## Details")
    out.append("")
    for m in _MOATS:
        out.append(f"### {m.id}. {m.name}")
        out.append("")
        out.append(f"**Value class:** {m.value}  ")
        out.append(f"**Status:** {m.status}")
        out.append("")
        out.append(m.description)
        out.append("")
        out.append("Implemented by:")
        for impl in m.implementers:
            out.append(f"- `{impl}`")
        out.append("")
        out.append("Grounded in residuals: " +
                   ", ".join(f"`{r}`" for r in m.residuals))
        out.append("")

    out.append("---")
    out.append("")
    out.append("## Status summary")
    out.append("")
    out.append("| Status | Count |")
    out.append("|--------|-------|")
    for st in sorted(set(m.status for m in _MOATS)):
        n = sum(1 for m in _MOATS if m.status == st)
        out.append(f"| {st} | {n} |")
    out.append("")

    out.append("## The register's own entry")
    out.append("")
    out.append("Moats 1 through 11 all terminate at `Ω`. The claim that")
    out.append("this set is complete cannot be decided from inside the")
    out.append("set. Adding moat 12 is the act of proceeding.")
    out.append("")
    return "\n".join(out)


def write_markdown(path: Path | None = None) -> Path:
    p = Path(path) if path else (
        Path(__file__).resolve().parent.parent.parent
        / "docs" / "moats.md"
    )
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render_markdown())
    return p


def evaluate_moats(
context=None):
    return {"context": dict(context or {}), "axes": {}, "score": 0.0}

