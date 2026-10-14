"""Layer engines — declarative logic dispatched by name.

A layer declares its engine and parameters in the manifest. The engine
module reads the manifest, walks the parameters, and produces the
artifact. Adding a layer is a manifest change; adding a new kind of
logic is an engine addition. The layers themselves are thin.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


# --------------------------------------------------------------------- helpers

def _walk(path: str, context: dict[str, Any], default: Any = None) -> Any:
    """Read a dotted path like 'A.unit' or 'input.requester' from context."""
    if not path:
        return default
    node: Any = context
    for part in path.split("."):
        if isinstance(node, dict):
            node = node.get(part, default)
        else:
            return default
        if node is None:
            return default
    return node


def _coerce(value: Any, kind: str | None) -> Any:
    if kind == "int":
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0
    if kind == "float":
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    if kind == "str":
        return str(value) if value is not None else ""
    return value


def _earlier_letters(context: dict[str, Any]) -> list[str]:
    return sorted(k for k in context.keys() if len(k) == 1 and k.isalpha())


# --------------------------------------------------------------------- engines

def derive_from_request(inputs: dict, context: dict, params: dict) -> dict:
    request = inputs.get("input") or {}
    mapping = params.get("mapping", {})
    types = params.get("types", {})
    out = {}
    for out_key, (in_key, fallback) in mapping.items():
        raw = request.get(in_key, fallback) if isinstance(request, dict) else fallback
        out[out_key] = _coerce(raw, types.get(out_key))
    return out


def bind_constraints(inputs: dict, context: dict, params: dict) -> dict:
    sources = params.get("sources", {})
    bound = {}
    for name, (letter, field) in sources.items():
        node = inputs.get(letter) or {}
        value = node.get(field) if isinstance(node, dict) else None
        bound[name] = {"value": value, "source": f"{letter}.{field}"}
    return {
        "quality": {"floor": bound.get("quality", {}).get("value", "unstated"), "source": bound.get("quality", {}).get("source", "")},
        "risk": {"ceiling": bound.get("risk", {}).get("value", "R3"), "source": bound.get("risk", {}).get("source", "")},
        "policy": {"binding": "none_declared", "source": "contract"},
        "budget": {"cap_usd": float(bound.get("budget", {}).get("value", 0.0) or 0.0), "source": bound.get("budget", {}).get("source", "")},
        "oversight": {"level": bound.get("oversight", {}).get("value", "none"), "source": bound.get("oversight", {}).get("source", "")},
    }


def compute_norm_curve(inputs: dict, context: dict, params: dict) -> dict:
    samples = _walk(params.get("samples_path", ""), context, None)
    if isinstance(samples, list) and samples:
        vals = sorted(float(x) for x in samples if isinstance(x, (int, float)))
        n = len(vals)
        median = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
        confidence = "high" if n >= 30 else "medium" if n >= 10 else "low"
        return {
            "median": median,
            "minimum": vals[0],
            "maximum": vals[-1],
            "sample_size": n,
            "confidence": confidence,
            "source": "observed",
        }
    return {"median": 0.0, "minimum": 0.0, "maximum": 0.0, "sample_size": 0, "confidence": "low", "source": "absent"}


def allocate_lowest_cost(inputs: dict, context: dict, params: dict) -> dict:
    candidates = _walk(params.get("candidates_path", ""), context, None)
    if not isinstance(candidates, list) or not candidates:
        candidates = [params.get("default_candidate", {"name": "default", "price": 0.0})]
    budget = float(_walk(params.get("budget_path", ""), context, 0.0) or 0.0)
    trace = []
    eligible = []
    for c in candidates:
        name = str(c.get("name", "unknown"))
        price = float(c.get("price", 0.0))
        trace.append(f"candidate {name} price {price} against budget {budget}")
        if price <= budget:
            eligible.append((price, name))
    if not eligible:
        return {"selected": "none", "price": 0.0, "trace": trace + ["no eligible candidate"]}
    eligible.sort()
    price, name = eligible[0]
    trace.append(f"selected {name} at {price}")
    return {"selected": name, "price": price, "trace": trace}


def compute_receipt(inputs: dict, context: dict, params: dict) -> dict:
    baseline = float(_walk(params.get("baseline_path", ""), context, 0.0) or 0.0)
    actual = float(_walk(params.get("actual_path", ""), context, 0.0) or 0.0)
    delta = baseline - actual
    return {
        "baseline_usd": baseline,
        "actual_usd": actual,
        "delta_usd": delta,
        "line_items": [{"item": "execution", "amount_usd": actual}],
    }


def wrap_envelope(inputs: dict, context: dict, params: dict) -> dict:
    wraps = params.get("wraps", [])
    payload = {w: context.get(w, {}) for w in wraps}
    integrity = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
    classification = _walk(params.get("classification_path", ""), context, "internal")
    if classification not in ("unclassified", "internal", "confidential", "secret"):
        classification = "internal"
    return {
        "schema_version": "1.0",
        "object_id": f"env-{integrity[:16]}",
        "correlation_id": str(context.get("correlation_id", "unset")),
        "classification": classification,
        "integrity": integrity,
    }


def score_fidelity(inputs: dict, context: dict, params: dict) -> dict:
    artifacts = params.get("artifacts", [])
    criteria = []
    scores = []
    for letter in artifacts:
        artifact = context.get(letter) or {}
        complete = bool(artifact) and all(v is not None for v in artifact.values())
        criteria.append(f"{letter}:complete" if complete else f"{letter}:incomplete")
        scores.append(1.0 if complete else 0.0)
    score = sum(scores) / len(scores) if scores else 0.0
    return {"score": score, "criteria": criteria}


def apply_gate_rules(inputs: dict, context: dict, params: dict) -> dict:
    threshold = float(params.get("threshold", 0.75))
    rules = []
    passed = True
    for rule in params.get("rules", []):
        name = rule.get("name", "unnamed")
        check = rule.get("check", "")
        if "A is not empty" in check:
            ok = bool(context.get("A"))
        elif "B is not empty" in check:
            ok = bool(context.get("B"))
        elif "G.score >= threshold" in check:
            ok = float(_walk("G.score", context, 0.0) or 0.0) >= threshold
        else:
            ok = False
        rules.append(f"{name}:{'pass' if ok else 'fail'}")
        passed = passed and ok
    return {"decision": "admit" if passed else "reject", "rules_checked": rules}


def bind_identity(inputs: dict, context: dict, params: dict) -> dict:
    return {
        "subject": str(_walk(params.get("subject_path", ""), context, "unknown")),
        "action": str(_walk(params.get("action_path", ""), context, "unknown")),
        "object": str(_walk(params.get("object_path", ""), context, "unknown")),
        "purpose": str(_walk(params.get("purpose_path", ""), context, "work")),
        "valid_until": str(_walk(params.get("valid_until_path", ""), context, "unknown")),
    }


def route_by_gate(inputs: dict, context: dict, params: dict) -> dict:
    gate = _walk(params.get("gate_path", ""), context, "reject")
    target = _walk(params.get("target_path", ""), context, "none")
    agent = _walk(params.get("agent_path", ""), context, "unknown")
    if gate != "admit":
        target = "none"
        agent = "none"
    return {
        "target": str(target),
        "agent": str(agent),
        "correlation_id": str(context.get("correlation_id", "unset")),
    }


def scope_jurisdiction(inputs: dict, context: dict, params: dict) -> dict:
    regimes = _walk(params.get("regimes_path", ""), context, [])
    if not isinstance(regimes, list):
        regimes = []
    return {
        "sovereign_domain": str(_walk(params.get("domain_path", ""), context, "local")),
        "residency": str(_walk(params.get("residency_path", ""), context, "unspecified")),
        "regimes": regimes,
    }


def classify_kind(inputs: dict, context: dict, params: dict) -> dict:
    kind = _walk(params.get("kind_path", ""), context, None)
    return {"kind": str(kind) if kind else "unclassified", "confidence": 1.0 if kind else 0.0}


def build_ledger(inputs: dict, context: dict, params: dict) -> dict:
    entries = []
    chain = ""
    for letter in _earlier_letters(context):
        payload_json = json.dumps(context[letter], sort_keys=True, default=str)
        ph = hashlib.sha256(payload_json.encode()).hexdigest()
        eh = hashlib.sha256((chain + letter + ph).encode()).hexdigest()
        entries.append({"letter": letter, "artifact_hash": ph, "entry_hash": eh, "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        chain = eh
    return {"entries": entries, "chain_head": chain}


def read_meter(inputs: dict, context: dict, params: dict) -> dict:
    telemetry = _walk(params.get("telemetry_path", ""), context, {}) or {}
    units = params.get("units", [])
    readings = []
    for unit in units:
        v = telemetry.get(unit) if isinstance(telemetry, dict) else None
        if v is not None:
            readings.append({"unit": unit, "quantity": float(v), "source": "telemetry"})
    return {"readings": readings}


def plan_oversight(inputs: dict, context: dict, params: dict) -> dict:
    valid = ("none", "notify", "approve-before", "approve-after", "escalate-on-anomaly", "continuous")
    level = _walk(params.get("level_path", ""), context, "none")
    if level not in valid:
        level = "none"
    checkpoints = []
    if level in ("approve-before", "approve-after"):
        checkpoints.append({"at": "pre-execution" if level == "approve-before" else "post-execution", "inspect": "execution-contract"})
    if level == "escalate-on-anomaly":
        checkpoints.append({"at": "on-anomaly", "inspect": "exception-record"})
    if level == "continuous":
        checkpoints.append({"at": "continuous", "inspect": "all-artifacts"})
    return {"level": level, "checkpoints": checkpoints}


def build_provenance(inputs: dict, context: dict, params: dict) -> dict:
    records = []
    chain = ""
    for letter in _earlier_letters(context):
        payload_json = json.dumps(context[letter], sort_keys=True, default=str)
        h = hashlib.sha256((chain + letter + payload_json).encode()).hexdigest()
        records.append({"layer": letter, "record_hash": h, "prev": chain})
        chain = h
    return {"records": records, "chain_head": chain}


def verdict_quality(inputs: dict, context: dict, params: dict) -> dict:
    signals = _walk(params.get("signals_path", ""), context, {}) or {}
    criteria = []
    for name, value in (signals.items() if isinstance(signals, dict) else []):
        criteria.append({"name": name, "value": value, "passed": bool(value)})
    if not criteria:
        return {"verdict": "partial", "criteria": []}
    passed = sum(1 for c in criteria if c["passed"])
    if passed == len(criteria):
        verdict = "pass"
    elif passed == 0:
        verdict = "fail"
    else:
        verdict = "partial"
    return {"verdict": verdict, "criteria": criteria}


def bound_risk(inputs: dict, context: dict, params: dict) -> dict:
    order = {"R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5}
    ceiling = _walk(params.get("ceiling_path", ""), context, "R3")
    quality = _walk(params.get("quality_path", ""), context, "partial")
    realized = ceiling if quality == "pass" else "R5"
    residual_idx = order.get(ceiling, 3) - order.get(realized, 5)
    residual = f"R{max(1, min(5, abs(residual_idx)))}"
    return {"ceiling": ceiling, "realized": realized, "residual": residual}


def propose_shadow(inputs: dict, context: dict, params: dict) -> dict:
    return {
        "proposed_allocation": str(_walk(params.get("allocation_path", ""), context, "none")),
        "projected_cost": float(_walk(params.get("price_path", ""), context, 0.0) or 0.0),
        "projected_quality": float(_walk(params.get("quality_path", ""), context, 0.0) or 0.0),
    }


def attest_artifacts(inputs: dict, context: dict, params: dict) -> dict:
    sources = params.get("sources", [])
    leaves = []
    for src in sources:
        node = _walk(src, context, [])
        if isinstance(node, list):
            for item in node:
                if isinstance(item, dict):
                    h = item.get("entry_hash") or item.get("record_hash")
                    if h:
                        leaves.append(h)
    if not leaves:
        root = ""
    else:
        while len(leaves) > 1:
            if len(leaves) % 2:
                leaves.append(leaves[-1])
            leaves = [hashlib.sha256((leaves[i] + leaves[i + 1]).encode()).hexdigest() for i in range(0, len(leaves), 2)]
        root = leaves[0]
    return {
        "run_id": str(context.get("correlation_id", "unset")),
        "artifact_root": root,
        "signer": "control-plane",
        "valid_until": str(context.get("input", {}).get("deadline", "unknown")),
    }


def attribute_usage(inputs: dict, context: dict, params: dict) -> dict:
    readings = _walk(params.get("readings_path", ""), context, []) or []
    account = str(_walk(params.get("account_path", ""), context, "unassigned"))
    attributions = []
    for r in readings:
        attributions.append({
            "account": account,
            "unit": r.get("unit", "unknown"),
            "quantity": float(r.get("quantity", 0.0)),
            "meter_ref": r.get("source", "unknown"),
        })
    return {"attributions": attributions}


def compute_variance(inputs: dict, context: dict, params: dict) -> dict:
    expected = float(_walk(params.get("norm_path", ""), context, 0.0) or 0.0)
    usage = _walk(params.get("usage_path", ""), context, []) or []
    target_unit = params.get("unit", "cost_usd")
    actual = sum(float(a.get("quantity", 0.0)) for a in usage if a.get("unit") == target_unit)
    delta = actual - expected
    pct = (delta / expected * 100.0) if expected else 0.0
    flag = "material" if abs(pct) > 200 else "notable" if abs(pct) > 100 else "within-norm"
    return {"variances": [{"dimension": target_unit, "expected": expected, "actual": actual, "delta": delta, "pct": pct, "flag": flag}]}


def witness_receipt(inputs: dict, context: dict, params: dict) -> dict:
    receipt = _walk(params.get("receipt_path", ""), context, {}) or {}
    trust = _walk(params.get("trust_path", ""), context, "")
    provenance = _walk(params.get("provenance_path", ""), context, "")
    baseline = float(receipt.get("baseline_usd", 0.0))
    actual = float(receipt.get("actual_usd", 0.0))
    reported = float(receipt.get("delta_usd", 0.0))
    recomputed = baseline - actual
    if abs(recomputed - reported) > 1e-9:
        verdict = "disputed"
    elif not trust or not provenance:
        verdict = "not-recomputable"
    else:
        verdict = "confirmed"
    return {"verdict": verdict, "receipt_hash": str(trust)}


def record_exception(inputs: dict, context: dict, params: dict) -> dict:
    rejections = _walk(params.get("rejections_path", ""), context, {})
    if not isinstance(rejections, dict) or not rejections:
        return {"origin_layer": "none", "failure_class": "none", "recovery": "terminate"}
    origin = next(iter(rejections))
    detail = rejections[origin]
    return {
        "origin_layer": str(origin),
        "failure_class": str(detail.get("status", "EXECUTION_FAILURE")) if isinstance(detail, dict) else "EXECUTION_FAILURE",
        "recovery": "escalate",
    }


def compute_yield(inputs: dict, context: dict, params: dict) -> dict:
    criteria = _walk(params.get("quality_path", ""), context, []) or []
    variances = _walk(params.get("variance_path", ""), context, []) or []
    total = len(criteria)
    passed = sum(1 for c in criteria if c.get("passed"))
    quality_yield = (passed / total) if total else 0.0
    cost_yield = 1.0
    if variances:
        pct = float(variances[0].get("pct", 0.0))
        cost_yield = max(0.0, 1.0 - abs(pct) / 100.0)
    composite = (quality_yield + cost_yield) / 2.0
    return {"quality_yield": quality_yield, "cost_yield": cost_yield, "composite_yield": composite}


def seal_zenith(inputs: dict, context: dict, params: dict) -> dict:
    letters = _earlier_letters(context)
    for letter in letters:
        payload = context[letter]
        if isinstance(payload, dict) and payload.get("_status") and payload["_status"] != "PASS":
            return {"run_id": str(context.get("correlation_id", "unset")), "artifact_hashes": [], "merkle_root": "", "signature": ""}
    hashes = []
    for letter in letters:
        payload_json = json.dumps(context[letter], sort_keys=True, default=str)
        hashes.append({"letter": letter, "hash": hashlib.sha256(payload_json.encode()).hexdigest()})
    leaves = [h["hash"] for h in hashes]
    if leaves:
        while len(leaves) > 1:
            if len(leaves) % 2:
                leaves.append(leaves[-1])
            leaves = [hashlib.sha256((leaves[i] + leaves[i + 1]).encode()).hexdigest() for i in range(0, len(leaves), 2)]
        root = leaves[0]
    else:
        root = ""
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    sig = hashlib.sha256(f"{root}{ts}".encode()).hexdigest()
    return {"run_id": str(context.get("correlation_id", "unset")), "artifact_hashes": hashes, "merkle_root": root, "signature": sig}


# --------------------------------------------------------------------- registry

ENGINE_REGISTRY = {
    "derive_from_request": derive_from_request,
    "bind_constraints": bind_constraints,
    "compute_norm_curve": compute_norm_curve,
    "allocate_lowest_cost": allocate_lowest_cost,
    "compute_receipt": compute_receipt,
    "wrap_envelope": wrap_envelope,
    "score_fidelity": score_fidelity,
    "apply_gate_rules": apply_gate_rules,
    "bind_identity": bind_identity,
    "route_by_gate": route_by_gate,
    "scope_jurisdiction": scope_jurisdiction,
    "classify_kind": classify_kind,
    "build_ledger": build_ledger,
    "read_meter": read_meter,
    "plan_oversight": plan_oversight,
    "build_provenance": build_provenance,
    "verdict_quality": verdict_quality,
    "bound_risk": bound_risk,
    "propose_shadow": propose_shadow,
    "attest_artifacts": attest_artifacts,
    "attribute_usage": attribute_usage,
    "compute_variance": compute_variance,
    "witness_receipt": witness_receipt,
    "record_exception": record_exception,
    "compute_yield": compute_yield,
    "seal_zenith": seal_zenith,
}


def run_engine(name: str, inputs: dict, context: dict, params: dict) -> dict:
    if name not in ENGINE_REGISTRY:
        raise NotImplementedError(f"engine {name!r} is not registered")
    return ENGINE_REGISTRY[name](inputs, context, params)
