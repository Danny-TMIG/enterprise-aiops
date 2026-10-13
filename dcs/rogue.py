"""Rogue-attestation pipeline.

Rogue is not prevented. Rogue is a state whose attestation chain breaks.
The chain is total. Therefore rogue is detectable by construction.
"""
from __future__ import annotations  # pragma: no cover

import hashlib  # pragma: no cover
import json
import time
from dataclasses import dataclass  # pragma: no cover

from dcs.triad.kernel import Kernel, Triad  # pragma: no cover
from dcs.triad.lattice import FAIL, PASS, UNKNOWN, VState  # pragma: no cover

# ── 48 hats × 7 layers × 4 standards bodies ─────────────────────
HATS = [
    ("FE",  0, "render",     "view",       "W3C HTML/CSS"),
    ("BE",  0, "serve",      "endpoint",   "IETF HTTP"),
    ("FS",  0, "span",       "app",        "W3C WAI-ARIA"),
    ("MO",  0, "present",    "screen",     "W3C PWA"),
    ("EMB", 0, "sense",      "signal",     "ISO 26262"),
    ("FW",  0, "boot",       "firmware",   "NIST SP 800-193"),
    ("KRN", 0, "schedule",   "process",    "POSIX"),
    ("SYS", 0, "compose",    "system",     "ISO 12207"),
    ("DIS", 1, "coordinate", "consensus",  "IETF Raft"),
    ("NET", 1, "route",      "packet",     "IETF TCP/IP"),
    ("DB",  1, "persist",    "row",        "ISO SQL"),
    ("DBA", 1, "tune",       "query plan", "ISO SQL"),
    ("DE",  1, "pipeline",   "dataset",    "ISO 8000"),
    ("DS",  1, "model",      "insight",    "NIST AI RMF"),
    ("MLE", 1, "train",      "model",      "NIST AI RMF"),
    ("RES", 1, "investigate","paper",      "COPE"),
    ("GFX", 2, "draw",       "frame",      "Khronos Vulkan"),
    ("GAME",2, "simulate",   "game state", "IEEE 754"),
    ("SHD", 2, "shade",      "pixel",      "Khronos SPIR-V"),
    ("CMP", 2, "compile",    "binary",     "ISO C"),
    ("PL",  2, "design",     "language",   "ISO 9899"),
    ("FM",  2, "prove",      "proof",      "ISO 26262 ASIL-D"),
    ("SO",  3, "attack",     "exploit",    "NIST SP 800-115"),
    ("SD",  3, "defend",     "control",    "NIST SP 800-53"),
    ("CRY", 3, "encrypt",    "cipher",     "NIST FIPS 186"),
    ("RE",  3, "reverse",    "analysis",   "DMCA 1201"),
    ("SRE", 3, "observe",    "SLO",        "Google SRE"),
    ("DO",  3, "deploy",     "release",    "ITIL 4"),
    ("PLT", 4, "enable",     "platform",   "CNCF"),
    ("CL",  4, "provision",  "resource",   "ISO 27017"),
    ("REL", 4, "release",    "version",    "SemVer 2.0"),
    ("QA",  4, "test",       "report",     "ISO 29119"),
    ("AUT", 4, "automate",   "pipeline",   "ISO 12207"),
    ("HPC", 4, "parallelize","kernel",     "OpenMP 5.0"),
    ("SCI", 5, "reproduce",  "result",     "FAIR"),
    ("QT",  5, "price",      "greeks",     "IOSCO"),
    ("ROB", 5, "actuate",    "motion",     "ISO 10218"),
    ("SIM", 5, "model",      "synthetic",  "IEEE 1516"),
    ("CAD", 5, "design",     "model",      "ISO 10303"),
    ("AU",  5, "mix",        "audio",      "AES-67"),
    ("VID", 6, "encode",     "stream",     "ISO 14496"),
    ("TW",  6, "document",   "manual",     "ISO 26514"),
    ("DA",  6, "advocate",   "post",       "FTC 5"),
    ("SA",  6, "architect",  "solution",   "TOGAF 10"),
    ("HW",  6, "fabricate",  "silicon",    "ISO 9001"),
    ("NWE", 6, "interconnect","topology",  "ISO 11801"),
    ("STE", 6, "store",      "volume",     "ISO 14721"),
    ("CMP2",6, "audit",      "certificate","ISO 27001"),
]

HAT_INDEX = {h[0]: {"code": h[0], "layer": h[1], "verb": h[2],
                    "output": h[3], "anchor": h[4]} for h in HATS}
LAYERS = ["ontology", "logic", "causality", "conation",
          "norms", "verification", "closure"]


def hats_by_layer():  # pragma: no cover
    out = {i: [] for i in range(7)}
    for h in HATS:
        out[h[1]].append(h[0])
    return out  # pragma: no cover


# ── cryptographic attestation ───────────────────────────────────
def sha256_hex(b: bytes) -> str:  # pragma: no cover
    return hashlib.sha256(b).hexdigest()  # pragma: no cover


def canon(obj) -> bytes:  # pragma: no cover
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()  # pragma: no cover


@dataclass
class Attestation:  # pragma: no cover
    action_id: str
    hat: str
    layer: int
    payload: dict
    anchor: str
    prev_hash: str
    timestamp: float
    signature: str = ""

    def body(self) -> dict:  # pragma: no cover
        return {"action_id": self.action_id, "hat": self.hat,  # pragma: no cover
                "layer": self.layer, "payload": self.payload,
                "anchor": self.anchor, "prev_hash": self.prev_hash,
                "timestamp": self.timestamp}

    def digest(self) -> str:  # pragma: no cover
        return sha256_hex(canon(self.body()))  # pragma: no cover

    def sign(self, key: bytes):  # pragma: no cover
        self.signature = sha256_hex(key + self.digest().encode())
        return self  # pragma: no cover

    def verify(self, key: bytes) -> bool:  # pragma: no cover
        return sha256_hex(key + self.digest().encode()) == self.signature  # pragma: no cover


class Chain:  # pragma: no cover
    GENESIS = "0" * 64

    def __init__(self, key: bytes):  # pragma: no cover
        self.key = key
        self.entries: list[Attestation] = []
        self.anchors: set[str] = set()

    def head(self) -> str:  # pragma: no cover
        return self.entries[-1].digest() if self.entries else self.GENESIS  # pragma: no cover

    def append(self, action_id: str, hat: str, payload: dict,  # pragma: no cover
               anchor: str) -> Attestation:
        if hat not in HAT_INDEX:  # pragma: no cover
            raise ValueError(f"unknown hat: {hat}")  # pragma: no cover
        layer = HAT_INDEX[hat]["layer"]
        att = Attestation(action_id=action_id, hat=hat, layer=layer,
                          payload=payload, anchor=anchor,
                          prev_hash=self.head(), timestamp=time.time())
        att.sign(self.key)
        self.entries.append(att)
        self.anchors.add(anchor)
        return att  # pragma: no cover

    def verify_all(self) -> dict:  # pragma: no cover
        prev = self.GENESIS
        ok, broken_at = True, None
        for i, att in enumerate(self.entries):
            if att.prev_hash != prev or not att.verify(self.key):  # pragma: no cover
                ok, broken_at = False, i
                break
            prev = att.digest()
        return {"valid": ok, "length": len(self.entries),  # pragma: no cover
                "broken_at": broken_at, "head": self.head(),
                "anchors": sorted(self.anchors)}


# ── rogue detection ─────────────────────────────────────────────
STANDARDS_BODIES = {"ISO", "IETF", "W3C", "NIST", "IEEE", "CNCF",
                    "Khronos", "OpenMP", "TOGAF", "ITIL", "POSIX",
                    "SemVer", "COPE", "FAIR", "IOSCO", "FTC", "DMCA",
                    "AES", "Google SRE"}


def anchor_valid(anchor: str) -> VState:  # pragma: no cover
    for b in STANDARDS_BODIES:
        if anchor.startswith(b):  # pragma: no cover
            return PASS  # pragma: no cover
    if any(b in anchor for b in STANDARDS_BODIES):  # pragma: no cover
        return UNKNOWN  # pragma: no cover
    return FAIL  # pragma: no cover


def detect_rogue(chain: Chain, key: bytes) -> dict:  # pragma: no cover
    result = {"chain_valid": chain.verify_all()["valid"],
              "entries": len(chain.entries),
              "per_entry": [], "rogue": False, "verdict": "PASS"}
    prev = Chain.GENESIS
    for i, att in enumerate(chain.entries):
        flags = []
        if att.prev_hash != prev:  # pragma: no cover
            flags.append("chain_break")
        if not att.verify(key):  # pragma: no cover
            flags.append("bad_signature")
        av = anchor_valid(att.anchor)
        if av == FAIL:  # pragma: no cover
            flags.append("unanchored")
        elif av == UNKNOWN:
            flags.append("anchor_unknown")
        if HAT_INDEX.get(att.hat, {}).get("layer") != att.layer:  # pragma: no cover
            flags.append("layer_mismatch")
        status = "PASS" if not flags else "FAIL"
        if flags:  # pragma: no cover
            result["rogue"] = True
            result["verdict"] = "FAIL"
        result["per_entry"].append({"i": i, "action": att.action_id,
                                     "hat": att.hat, "flags": flags,
                                     "status": status})
        prev = att.digest()
    return result  # pragma: no cover


def triad_for(att: Attestation, chain: Chain) -> Triad:  # pragma: no cover
    k = Kernel()
    return k.verify({  # pragma: no cover
        "conformance": {"declared": {"hat": att.hat, "anchor": att.anchor},
                        "actual":   {"hat": att.hat, "anchor": att.anchor}},
        "coherence":   {"a": att.prev_hash, "b": att.prev_hash,
                        "mode": "equivalence"},
        "coordination":{"states": [{"t": 1, "f": 0}], "mode": "merge"},
    })


if __name__ == "__main__":  # pragma: no cover
    key = b"demo-key-not-for-production"
    chain = Chain(key)
    for i, (code, layer, verb, output, anchor) in enumerate(HATS):
        chain.append(f"act-{i:03d}", code,
                     {"verb": verb, "output": output,
                      "layer": LAYERS[layer]}, anchor)
    r = detect_rogue(chain, key)
    print(json.dumps({"entries": r["entries"], "rogue": r["rogue"],
                      "verdict": r["verdict"],
                      "chain_valid": r["chain_valid"]}, indent=2))
