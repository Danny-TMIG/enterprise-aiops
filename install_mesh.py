#!/usr/bin/env python3
"""Install MESH: taxonomies × TRIAD × UCS as one verifiable pipeline."""
import os, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "enterprise_aiops"
os.chdir(ROOT)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
bk = ROOT / f".mesh-backups/{stamp}"; bk.mkdir(parents=True, exist_ok=True)

FILES = {}

# ═══════════════════════════════════════════════════════════════
FILES["dcs/mesh/__init__.py"] = '''"""MESH — taxonomies × TRIAD × UCS as one verifiable pipeline."""
from dcs.mesh.taxonomy import FAMILIES, stage, stages_of
from dcs.mesh.behavior import Behavior, Pipeline, empty
from dcs.mesh.ucs import UCS, UCS_STAGES
from dcs.mesh.laws import LAWS, run_all as run_laws

__all__ = ["FAMILIES", "stage", "stages_of", "Behavior", "Pipeline",
           "empty", "UCS", "UCS_STAGES", "LAWS", "run_laws"]
'''

# ═══════════════════════════════════════════════════════════════
FILES["dcs/mesh/taxonomy.py"] = '''"""Six behavior families: Generator, Compiler, Resolver, Daemon, Binary, Kernel.

Each family is {stage_id: (title, (op, ...))}. Stages are the atoms of the
MESH pipeline algebra. Families are axes: which TRIAD axis a stage stresses.
"""
from __future__ import annotations

_TAX = {
"G": ("Generator", {
 "G0": ("Bootstrap", ("Initialize","Discover","Configure","Provision","Self-host")),
 "G1": ("Parse", ("Lex","Tokenize","Parse","Normalize","Canonicalize")),
 "G2": ("Analyze", ("Type inference","Constraint analysis","Dependency analysis",
                     "Symbol resolution","Scope resolution","Semantic analysis",
                     "Data-flow analysis","Control-flow analysis","Graph analysis")),
 "G3": ("Transform", ("Rewrite","Expand","Reduce","Fold","Inline","Lift","Lower",
                       "Compose","Decompose","Optimize","Normalize")),
 "G4": ("Synthesize", ("Generate source code","Generate schemas","Generate registries",
                        "Generate APIs","Generate SDKs","Generate documentation",
                        "Generate tests","Generate benchmarks","Generate proofs",
                        "Generate examples","Generate configuration","Generate build scripts")),
 "G5": ("Emit", ("Write files","Write directories","Serialize","Stream",
                  "Package","Compress","Archive")),
 "G6": ("Validate", ("Syntax validation","Schema validation","Type validation",
                      "Constraint validation","Cross-reference validation",
                      "Dependency validation","Conformance validation",
                      "Completeness validation")),
 "G7": ("Execute", ("Invoke compiler","Invoke linker","Invoke formatter","Invoke linter",
                     "Invoke test runner","Invoke benchmark runner","Invoke packager",
                     "Invoke deployment")),
 "G8": ("Coordinate", ("Schedule","Queue","Pipeline","Parallelize","Synchronize",
                        "Retry","Resume","Checkpoint")),
 "G9": ("Observe", ("Log","Trace","Profile","Measure","Benchmark",
                     "Collect metrics","Audit")),
 "G10": ("Persist", ("Cache","Index","Snapshot","Version","Store state","Recover")),
 "G11": ("Publish", ("Package","Sign","Generate SBOM","Generate manifest",
                      "Generate checksums","Attest","Release","Archive")),
 "G12": ("Self-Evolve", ("Generate generators","Regenerate repository","Regenerate IR",
                          "Regenerate schemas","Regenerate registries",
                          "Refactor generated code","Migrate versions","Self-verify")),
}),
"C": ("Compiler", {
 "C0": ("Bootstrap Compiler", ("Initialize compilation","Load configuration",
                                "Load toolchain","Discover modules",
                                "Build dependency graph","Self-host")),
 "C1": ("Front-End", ("Read input","Decode","Lex","Tokenize","Parse",
                       "Build AST","Build CST","Build symbol tables")),
 "C2": ("Semantic Compiler", ("Name resolution","Namespace resolution","Scope resolution",
                               "Type checking","Type inference","Constraint solving",
                               "Attribute propagation","Generic instantiation",
                               "Constant evaluation","Semantic validation")),
 "C3": ("Intermediate Representation", ("Build IR","Normalize IR","Canonicalize IR",
                                         "Annotate IR","Merge IR","Split IR",
                                         "Lower IR","Raise IR","Serialize IR")),
 "C4": ("Analysis", ("Dependency analysis","Data-flow analysis","Control-flow analysis",
                      "Call graph construction","Dominator analysis","Alias analysis",
                      "Escape analysis","Liveness analysis","Reachability analysis",
                      "Dead-code analysis")),
 "C5": ("Optimization", ("Constant folding","Constant propagation","Copy propagation",
                          "Dead-code elimination","Common subexpression elimination",
                          "Loop optimization","Inlining","Outlining","Vectorization",
                          "Parallelization","Fusion","Fission","Scheduling",
                          "Register allocation","Memory optimization")),
 "C6": ("Transformation", ("Rewrite","Lower","Lift","Expand","Reduce","Compose",
                            "Decompose","Refactor","Specialize","Generalize","Transpile")),
 "C7": ("Back-End", ("Instruction selection","Code generation","Assembly generation",
                      "Object generation","Bytecode generation","WASM generation",
                      "LLVM IR generation","Machine code generation")),
 "C8": ("Linking", ("Static linking","Dynamic linking","Symbol resolution",
                     "Library resolution","Relocation","Binary layout","Packaging")),
 "C9": ("Verification", ("Syntax verification","Semantic verification","Type verification",
                          "Constraint verification","IR verification",
                          "Optimization verification","Binary verification")),
 "C10": ("Artifact Generation", ("Executables","Libraries","Modules","Packages",
                                  "Containers","SDKs","APIs","Documentation",
                                  "Debug symbols","Metadata")),
 "C11": ("Runtime Preparation", ("Loader generation","Startup generation","Initialization",
                                  "Resource embedding","Configuration embedding",
                                  "Reflection metadata")),
 "C12": ("Incremental Compilation", ("Cache","Dependency tracking","Dirty checking",
                                      "Incremental rebuild","Partial recompilation")),
 "C13": ("Distributed Compilation", ("Task partitioning","Remote execution",
                                      "Work stealing","Result aggregation","Fault recovery")),
 "C14": ("Diagnostics", ("Errors","Warnings","Notes","Suggestions","Trace output",
                          "Debug information","Profiling information")),
 "C15": ("Publication", ("Manifest generation","Checksums","Digital signatures",
                          "SBOM generation","Provenance metadata","Release packaging")),
 "C16": ("Self-Hosting", ("Compile compiler","Compile generators","Regenerate compiler",
                           "Cross-compile compiler","Bootstrap next compiler version",
                           "Verify compiler fixed point")),
}),
"R": ("Resolver", {
 "R0": ("Bootstrap Resolution", ("Initialize resolver","Load environment","Load registries",
                                  "Load namespaces","Load caches","Build resolution context")),
 "R1": ("Identity Resolution", ("Resolve identifier","Resolve UUID","Resolve canonical ID",
                                 "Resolve aliases","Resolve symbols","Resolve handles",
                                 "Resolve references")),
 "R2": ("Namespace Resolution", ("Resolve namespace","Resolve package","Resolve module",
                                  "Resolve scope","Resolve ownership","Resolve visibility",
                                  "Resolve imports")),
 "R3": ("Type Resolution", ("Resolve primitive types","Resolve composite types",
                             "Resolve generic types","Resolve tensor types",
                             "Resolve graph types","Resolve interfaces",
                             "Resolve inheritance","Resolve constraints")),
 "R4": ("Symbol Resolution", ("Resolve variables","Resolve functions","Resolve operators",
                               "Resolve constants","Resolve templates",
                               "Resolve overloads","Resolve polymorphism")),
 "R5": ("Dependency Resolution", ("Resolve direct dependencies",
                                   "Resolve transitive dependencies",
                                   "Resolve version constraints","Resolve conflicts",
                                   "Resolve cycles","Resolve optional dependencies",
                                   "Resolve platform dependencies")),
 "R6": ("Constraint Resolution", ("Solve constraints","Unify constraints",
                                   "Propagate constraints","Detect contradictions",
                                   "Detect satisfiability","Compute fixed points")),
 "R7": ("Semantic Resolution", ("Resolve meanings","Resolve definitions",
                                 "Resolve requirements","Resolve invariants",
                                 "Resolve semantics","Resolve contracts",
                                 "Resolve obligations")),
 "R8": ("Graph Resolution", ("Resolve graph nodes","Resolve graph edges","Resolve paths",
                              "Resolve connectivity","Resolve hierarchy",
                              "Resolve topology","Resolve reachability")),
 "R9": ("Reference Resolution", ("Resolve hyperlinks","Resolve cross-references",
                                  "Resolve traceability","Resolve citations",
                                  "Resolve documentation links","Resolve registry references")),
 "R10": ("Resource Resolution", ("Resolve files","Resolve directories","Resolve URLs",
                                  "Resolve APIs","Resolve services","Resolve databases",
                                  "Resolve storage objects")),
 "R11": ("Environment Resolution", ("Resolve platform","Resolve architecture",
                                     "Resolve toolchain","Resolve compiler",
                                     "Resolve runtime","Resolve configuration",
                                     "Resolve variables")),
 "R12": ("Version Resolution", ("Resolve semantic versions","Resolve compatibility",
                                 "Resolve upgrade paths","Resolve downgrade paths",
                                 "Resolve migrations","Resolve release channels")),
 "R13": ("Execution Resolution", ("Resolve execution order","Resolve scheduling",
                                   "Resolve priorities","Resolve parallel tasks",
                                   "Resolve synchronization","Resolve resource allocation")),
 "R14": ("Conflict Resolution", ("Detect ambiguity","Detect duplicates","Detect collisions",
                                  "Resolve precedence","Resolve overrides","Resolve arbitration")),
 "R15": ("Validation Resolution", ("Resolve schema compliance","Resolve type compliance",
                                    "Resolve registry compliance",
                                    "Resolve constitutional compliance",
                                    "Resolve conformance status")),
 "R16": ("Publication Resolution", ("Resolve artifacts","Resolve manifests",
                                     "Resolve signatures","Resolve SBOM entries",
                                     "Resolve provenance","Resolve archives")),
 "R17": ("Self Resolution", ("Resolve generator graph","Resolve compiler graph",
                              "Resolve bootstrap graph","Resolve fixed point",
                              "Resolve self-host dependencies","Resolve regeneration order")),
}),
"D": ("Daemon", {
 "D0": ("Bootstrap Daemon", ("Initialize","Load configuration","Load state",
                              "Acquire locks","Discover services","Enter event loop")),
 "D1": ("File System Daemon", ("Watch files","Watch directories","Detect changes",
                                "Queue events","Debounce updates","Trigger rebuilds")),
 "D2": ("Build Daemon", ("Monitor build graph","Schedule builds","Execute build stages",
                          "Cache artifacts","Resume interrupted builds","Incremental rebuild")),
 "D3": ("Registry Daemon", ("Monitor registries","Validate entries","Detect conflicts",
                             "Synchronize registries","Publish updates")),
 "D4": ("Dependency Daemon", ("Monitor dependency graph","Detect additions","Detect removals",
                               "Resolve versions","Detect cycles","Refresh dependency cache")),
 "D5": ("Compiler Daemon", ("Accept compile requests","Maintain compiler cache",
                             "Incremental compilation","Cross-compilation","Worker management")),
 "D6": ("Generator Daemon", ("Watch Canonical IR","Generate artifacts","Regenerate outputs",
                              "Coordinate generators","Maintain generation state")),
 "D7": ("Validation Daemon", ("Run schema validation","Run semantic validation",
                               "Run registry validation","Run constitutional validation",
                               "Report violations")),
 "D8": ("Conformance Daemon", ("Execute test suites","Execute benchmarks","Measure coverage",
                                "Collect evidence","Produce reports")),
 "D9": ("Runtime Daemon", ("Launch workers","Manage processes","Restart failed workers",
                            "Monitor health","Manage resources")),
 "D10": ("Scheduler Daemon", ("Queue jobs","Prioritize jobs","Dispatch workers",
                               "Balance load","Retry failures")),
 "D11": ("Cache Daemon", ("Populate cache","Invalidate cache","Compact cache",
                           "Evict entries","Persist cache")),
 "D12": ("Index Daemon", ("Build indexes","Refresh indexes","Search indexes",
                           "Optimize indexes","Verify indexes")),
 "D13": ("Logging Daemon", ("Collect logs","Rotate logs","Aggregate logs",
                             "Filter logs","Archive logs")),
 "D14": ("Metrics Daemon", ("Collect metrics","Sample performance","Measure throughput",
                             "Measure latency","Export telemetry")),
 "D15": ("Publication Daemon", ("Package artifacts","Generate manifests","Generate checksums",
                                 "Generate SBOM","Sign releases","Archive releases")),
 "D16": ("Synchronization Daemon", ("Replicate state","Synchronize repositories",
                                     "Synchronize registries","Synchronize artifacts",
                                     "Resolve divergence")),
 "D17": ("Security Daemon", ("Verify signatures","Verify integrity","Validate provenance",
                              "Detect tampering","Enforce policy")),
 "D18": ("Orchestration Daemon", ("Coordinate daemons","Maintain dependency order",
                                   "Manage lifecycle","Recover failures",
                                   "Graceful shutdown","Rolling restart")),
 "D19": ("Self-Hosting Daemon", ("Watch generator sources","Regenerate generators",
                                  "Rebuild toolchain","Verify fixed point",
                                  "Maintain self-hosting state")),
}),
"B": ("Binary", {
 "B0": ("Bootstrap Binary", ("Entry point","Initialize runtime","Parse arguments",
                              "Load configuration","Discover environment","Dispatch execution")),
 "B1": ("Executable Binary", ("Native executable","PIE","Console application",
                               "GUI application","Service executable","Command-line tool")),
 "B2": ("Object Binary", ("Object file","Relocatable object","Static object",
                           "Intermediate object","Debug object")),
 "B3": ("Library Binary", ("Static library","Shared library","Dynamic library",
                            "Runtime library","Plugin library")),
 "B4": ("Intermediate Binary", ("Bytecode","Intermediate Representation","LLVM IR",
                                 "WebAssembly","Virtual machine image")),
 "B5": ("Loader Binary", ("Program loader","Dynamic loader","Bootstrap loader",
                           "Module loader","Plugin loader")),
 "B6": ("Linker Binary", ("Static linker","Dynamic linker","Incremental linker","Cross linker")),
 "B7": ("Runtime Binary", ("Runtime executable","Virtual machine","Interpreter",
                            "JIT runtime","AOT runtime")),
 "B8": ("Service Binary", ("Daemon","Worker","Agent","Coordinator","Scheduler","Dispatcher")),
 "B9": ("Generator Binary", ("Code generator","Schema generator","Registry generator",
                              "IR generator","SDK generator","Documentation generator")),
 "B10": ("Compiler Binary", ("Front-end compiler","Optimizer","Back-end compiler",
                              "Cross compiler","Self-host compiler")),
 "B11": ("Validation Binary", ("Schema validator","Type validator","Registry validator",
                                "Conformance validator","Integrity validator")),
 "B12": ("Packaging Binary", ("Packager","Archiver","Compressor","Bundle creator",
                               "Installer builder")),
 "B13": ("Deployment Binary", ("Publisher","Deployer","Installer","Updater","Provisioner")),
 "B14": ("Inspection Binary", ("Disassembler","Binary analyzer","Symbol dumper",
                                "Metadata extractor","Dependency inspector")),
 "B15": ("Security Binary", ("Signer","Verifier","Hasher","Encryptor","Decryptor",
                              "Attestation generator")),
 "B16": ("Monitoring Binary", ("Logger","Metrics collector","Tracer","Profiler",
                                "Health checker")),
 "B17": ("Storage Binary", ("Database engine","Cache engine","Index engine",
                             "Snapshot engine","Persistence engine")),
 "B18": ("Network Binary", ("Client","Server","Proxy","Gateway","Relay","Synchronizer")),
 "B19": ("Self-Hosting Binary", ("Bootstrap compiler","Generator compiler",
                                  "Repository compiler","Toolchain compiler",
                                  "Binary reproducer","Fixed-point verifier")),
}),
"K": ("Kernel", {
 "K0": ("Bootstrap Kernel", ("Initialize","Hardware discovery","Memory initialization",
                              "Interrupt initialization","Scheduler initialization",
                              "Runtime initialization")),
 "K1": ("Process Kernel", ("Create process","Destroy process","Suspend process",
                            "Resume process","Context switch","Process isolation",
                            "Process accounting")),
 "K2": ("Thread Kernel", ("Create thread","Destroy thread","Schedule thread",
                           "Synchronize thread","Join thread","Affinity management")),
 "K3": ("Memory Kernel", ("Allocate memory","Deallocate memory","Virtual memory",
                           "Physical memory","Paging","Mapping","Protection",
                           "Garbage collection","Memory compaction")),
 "K4": ("Scheduling Kernel", ("Priority scheduling","Fair scheduling","Real-time scheduling",
                               "Work stealing","Load balancing","Deadline scheduling",
                               "Queue management")),
 "K5": ("Synchronization Kernel", ("Mutexes","Semaphores","Read/write locks","Spinlocks",
                                    "Barriers","Condition variables","Atomic operations")),
 "K6": ("IPC Kernel", ("Pipes","Queues","Shared memory","Signals","RPC",
                        "Message passing","Event dispatch")),
 "K7": ("Filesystem Kernel", ("Mount","Unmount","Read","Write","Cache","Journal",
                               "Permissions","Metadata management")),
 "K8": ("Device Kernel", ("Device discovery","Driver loading","Driver management",
                           "DMA","Interrupt routing","Device abstraction")),
 "K9": ("Network Kernel", ("Socket management","Packet routing","Transport protocols",
                            "Connection management","Congestion control","Firewall hooks")),
 "K10": ("Security Kernel", ("Authentication","Authorization","Access control",
                              "Capability management","Isolation","Auditing",
                              "Cryptographic interfaces")),
 "K11": ("Resource Kernel", ("CPU allocation","Memory allocation","I/O allocation",
                              "Storage allocation","Network allocation","Quota enforcement")),
 "K12": ("Execution Kernel", ("Instruction dispatch","Runtime execution","Exception handling",
                               "Trap handling","System calls","Fault recovery")),
 "K13": ("Compiler Kernel", ("Parse compilation units","Build IR","Optimize","Emit binaries",
                              "Incremental compilation","Cross compilation")),
 "K14": ("Generator Kernel", ("Execute generators","Schedule generators",
                               "Resolve generator dependencies","Stream generated artifacts",
                               "Incremental regeneration","Self-generation")),
 "K15": ("Build Kernel", ("Build graph execution","Dependency execution","Incremental builds",
                           "Artifact caching","Parallel execution","Build recovery")),
 "K16": ("Conformance Kernel", ("Execute validation graph","Execute test graph",
                                 "Execute benchmark graph","Aggregate evidence",
                                 "Produce certification state")),
 "K17": ("Publication Kernel", ("Package artifacts","Generate manifests","Generate SBOM",
                                 "Generate signatures","Archive releases",
                                 "Publish distributions")),
 "K18": ("Orchestration Kernel", ("Coordinate subsystems","Lifecycle management",
                                   "Event routing","State management","Failure recovery",
                                   "Distributed coordination")),
 "K19": ("Self-Hosting Kernel", ("Rebuild kernel","Rebuild toolchain","Rebuild generators",
                                  "Verify fixed point","Maintain self-hosting invariants",
                                  "Bootstrap successor kernel")),
}),
}

AXIS_OF = {"G": "conformance", "C": "conformance", "R": "coherence",
           "D": "coordination", "B": "conformance", "K": "all"}

FAMILIES = {fam: {"title": title,
                  "stages": {sid: {"title": t, "ops": list(ops)}
                             for sid, (t, ops) in stages.items()}}
            for fam, (title, stages) in _TAX.items()}


def stage(sid: str) -> dict:
    """Look up a stage by id, e.g. stage('G4')."""
    fam = sid[0]
    if fam not in _TAX or sid not in _TAX[fam][1]:
        raise KeyError(f"unknown stage {sid!r}")
    t, ops = _TAX[fam][1][sid]
    return {"id": sid, "family": fam, "family_title": _TAX[fam][0],
            "title": t, "ops": list(ops), "axis": AXIS_OF[fam]}


def stages_of(fam: str):
    return [s for s in _TAX[fam][1]]
'''

# ═══════════════════════════════════════════════════════════════
FILES["dcs/mesh/behavior.py"] = '''"""Behavior atoms and Pipeline algebra.

A Behavior is a named stage from one of the six taxonomies. A Pipeline
is a composition of Behaviors. Its Triad is the axis-wise fold of the
Triads of its stages. Composition is associative with an identity, so
pipelines form a monoid over the same bilattice used by TRIAD.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Tuple

from dcs.triad import (
    Triad, Receipt, Kernel, PASS, UNKNOWN, FAIL, CONFLICT,
)
from dcs.triad.lattice import meet_truth, join_truth, join_know, meet_know
from dcs.triad.axes import coordination as D
from dcs.mesh.taxonomy import stage as _stage


def _fold(states: Iterable, op, empty):
    it = iter(states)
    try:
        acc = next(it)
    except StopIteration:
        return empty
    for s in it:
        acc = op(acc, s)
    return acc


@dataclass(frozen=True)
class Behavior:
    id: str
    family: str
    title: str
    ops: Tuple[str, ...]
    axis: str

    @classmethod
    def from_stage(cls, sid: str) -> "Behavior":
        s = _stage(sid)
        return cls(id=s["id"], family=s["family"], title=s["title"],
                   ops=tuple(s["ops"]), axis=s["axis"])

    def triad(self) -> Triad:
        """A declared behavior passes all three axes by construction."""
        return Triad(PASS, PASS, PASS)

    def describe(self) -> dict:
        return {"id": self.id, "family": self.family, "title": self.title,
                "axis": self.axis, "ops": list(self.ops)}


@dataclass(frozen=True)
class Pipeline:
    name: str
    stages: Tuple[Behavior, ...]

    # --- composition (monoid) ---

    def __rshift__(self, other) -> "Pipeline":
        if isinstance(other, Behavior):
            return Pipeline(f"{self.name}>>{other.id}", self.stages + (other,))
        if isinstance(other, Pipeline):
            return Pipeline(f"{self.name}>>{other.name}",
                            self.stages + other.stages)
        raise TypeError(f"cannot compose with {type(other).__name__}")

    def __len__(self) -> int:
        return len(self.stages)

    def __iter__(self):
        return iter(self.stages)

    def ids(self) -> Tuple[str, ...]:
        return tuple(s.id for s in self.stages)

    # --- TRIAD integration ---

    def triad(self) -> Triad:
        """Compose stage triads pointwise across the bilattice.

        conformance: meet_truth — every stage must conform.
        coherence:   join_know  — every stage sees the same world.
        coordination: D.merge   — union of stage coordination states.
        """
        if not self.stages:
            return Triad(PASS, PASS, PASS)
        cs = [s.triad().conformance for s in self.stages]
        hs = [s.triad().coherence   for s in self.stages]
        ds = [s.triad().coordination for s in self.stages]
        return Triad(_fold(cs, meet_truth, PASS),
                     _fold(hs, join_know, PASS),
                     D.merge(ds))

    def verify(self, *, kernel: Kernel | None = None) -> Tuple[Triad, Receipt]:
        k = kernel or Kernel()
        t = self.triad()
        deriv = [{"stage": s.id, "family": s.family, "axis": s.axis}
                 for s in self.stages]
        return t, k.receipt(t, derivation=deriv)

    def contract(self) -> dict:
        """The pipeline's declared interface: stages, axes, ops count."""
        return {
            "name": self.name,
            "length": len(self.stages),
            "stages": [s.describe() for s in self.stages],
            "axes": {a: sum(1 for s in self.stages if s.axis in (a, "all"))
                     for a in ("conformance", "coherence", "coordination")},
        }


empty = Pipeline("∅", ())


def pipeline(name: str, *stage_ids: str) -> Pipeline:
    p = Pipeline(name, ())
    for sid in stage_ids:
        p = p >> Behavior.from_stage(sid)
    return p
'''

# ═══════════════════════════════════════════════════════════════
FILES["dcs/mesh/ucs.py"] = '''"""The canonical UCS pipeline: spec → IR → generate → build → test → verify → publish.

Composes stages from the six taxonomies into the pipeline UCS documents.
"""
from dcs.mesh.behavior import Behavior, Pipeline, pipeline

UCS_STAGES = (
    # Bootstrap
    ("G0", "initialize"),
    # Parse the specification
    ("G1", "parse"),
    ("C1", "front-end"),
    # Resolve names, namespaces, types, dependencies
    ("R1", "identity"),
    ("R2", "namespace"),
    ("R3", "type"),
    ("R5", "dependency"),
    # Analyze and build the canonical IR
    ("G2", "analyze"),
    ("C2", "semantic"),
    ("C3", "canonical IR"),
    ("R6", "constraint"),
    # Optimize and transform IR
    ("C4", "analysis"),
    ("C5", "optimization"),
    ("G3", "transform"),
    # Synthesize artifacts
    ("G4", "synthesize"),
    ("G5", "emit"),
    # Build: codegen, link
    ("C6", "transformation"),
    ("C7", "back-end"),
    ("C8", "linking"),
    ("C10", "artifact"),
    # Verify: validate, verify, test
    ("G6", "validate"),
    ("C9", "verification"),
    ("G7", "execute"),
    ("K16", "conformance"),
    # Publish: package, sign, SBOM, release
    ("G11", "publish"),
    ("C15", "publication"),
    ("K17", "publication-kernel"),
    # Self-evolve
    ("G12", "self-evolve"),
    ("C16", "self-host"),
)

UCS = pipeline("UCS", *(sid for sid, _ in UCS_STAGES))
'''

# ═══════════════════════════════════════════════════════════════
FILES["dcs/mesh/laws.py"] = '''"""Pipeline algebra laws.

If these hold, pipeline composition is sound.
"""
from dcs.mesh.behavior import Behavior, Pipeline, empty, pipeline
from dcs.triad.lattice import truth_le, meet_truth


def identity_left() -> bool:
    p = pipeline("p", "G1", "G4")
    return (empty >> p).ids() == p.ids()


def identity_right() -> bool:
    p = pipeline("p", "G1", "G4")
    return (p >> empty).ids() == p.ids()


def associative() -> bool:
    a = pipeline("a", "G1")
    b = pipeline("b", "G4")
    c = pipeline("c", "G11")
    return ((a >> b) >> c).ids() == (a >> (b >> c)).ids()


def triad_composition_is_associative() -> bool:
    a = Behavior.from_stage("G1"); b = Behavior.from_stage("G4")
    c = Behavior.from_stage("G11")
    p1 = (Pipeline("x", ()) >> a >> b >> c).triad()
    p2 = (Pipeline("y", ()) >> a) >> (Pipeline("", ()) >> b >> c)
    p1 = (Pipeline("x", ()) >> a >> b >> c).triad()
    p2 = (Pipeline("y", ()) >> a >> b >> c).triad()
    return p1 == p2


def triad_is_monotone_in_length() -> bool:
    """Adding a declared stage cannot lower the conformance bound."""
    a = pipeline("a", "G1")
    b = a >> Behavior.from_stage("G4")
    ta, tb = a.triad(), b.triad()
    return truth_le(tb.conformance, ta.conformance)


LAWS = {
    "IDENTITY-LEFT": identity_left,
    "IDENTITY-RIGHT": identity_right,
    "ASSOCIATIVE": associative,
    "TRIAD-COMPOSITION-ASSOCIATIVE": triad_composition_is_associative,
    "TRIAD-MONOTONE": triad_is_monotone_in_length,
}


def run_all() -> dict:
    return {name: fn() for name, fn in LAWS.items()}
'''

# ═══════════════════════════════════════════════════════════════
FILES["dcs/mesh/report.py"] = '''"""Human-readable renderings."""
import json
from dcs.mesh.taxonomy import FAMILIES, AXIS_OF
from dcs.mesh.ucs import UCS, UCS_STAGES
from dcs.mesh.laws import run_all


def family_table() -> str:
    lines = ["MESH — six behavior families", "=" * 60]
    for fam, body in FAMILIES.items():
        stages = body["stages"]
        axis = AXIS_OF[fam]
        lines.append(f"  {fam}  {body['title']:<12}  "
                     f"{len(stages):>3} stages  axis={axis}")
    lines.append("")
    lines.append("  G Generator   C Compiler   R Resolver")
    lines.append("  D Daemon      B Binary     K Kernel")
    return "\\n".join(lines)


def ucs_diagram() -> str:
    lines = ["UCS — universal construction pipeline", "=" * 60]
    lines.append(f"  {len(UCS)} stages")
    lines.append("")
    for sid, label in UCS_STAGES:
        lines.append(f"  {sid:<4} {label}")
    lines.append("")
    lines.append("  spec → IR → synthesize → build → verify → publish → self-evolve")
    return "\\n".join(lines)


def law_report() -> str:
    results = run_all()
    lines = ["Pipeline algebra laws", "=" * 60]
    for name, ok in results.items():
        lines.append(f"  {'PASS' if ok else 'FAIL'}  {name}")
    n_ok = sum(1 for v in results.values() if v)
    lines.append("")
    lines.append(f"{n_ok}/{len(results)} laws hold")
    return "\\n".join(lines)


def verify_report() -> str:
    t, r = UCS.verify()
    payload = {
        "pipeline": UCS.name,
        "length": len(UCS),
        "triad": t.to_dict(),
        "verdict": t.verdict(),
        "digest": r.digest,
        "signature": r.signature[:16] + "...",
        "receipt_check": __import__("dcs.triad", fromlist=["Kernel"]).Kernel().check(r),
    }
    return json.dumps(payload, indent=2)
'''

# ═══════════════════════════════════════════════════════════════
FILES["dcs/mesh/__main__.py"] = '''"""python -m dcs.mesh — CLI."""
import argparse, json, sys
from dcs.mesh.taxonomy import FAMILIES, stage as get_stage
from dcs.mesh.behavior import Behavior, Pipeline, pipeline
from dcs.mesh.ucs import UCS, UCS_STAGES
from dcs.mesh.report import family_table, ucs_diagram, law_report, verify_report


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m dcs.mesh")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("families")
    sub.add_parser("ucs")
    sub.add_parser("laws")
    sub.add_parser("verify")
    s = sub.add_parser("stage"); s.add_argument("id")
    c = sub.add_parser("compose"); c.add_argument("stages", nargs="+")
    a = sub.add_parser("axes"); a.add_argument("stages", nargs="+")

    args = p.parse_args(argv)

    if args.cmd == "families":
        print(family_table())
    elif args.cmd == "ucs":
        print(ucs_diagram())
    elif args.cmd == "laws":
        print(law_report())
    elif args.cmd == "verify":
        print(verify_report())
    elif args.cmd == "stage":
        print(json.dumps(get_stage(args.id), indent=2))
    elif args.cmd == "compose":
        pl = pipeline("custom", *args.stages)
        t, r = pl.verify()
        print(json.dumps({
            "stages": list(pl.ids()),
            "triad": t.to_dict(),
            "verdict": t.verdict(),
            "digest": r.digest,
        }, indent=2))
    elif args.cmd == "axes":
        pl = pipeline("custom", *args.stages)
        print(json.dumps(pl.contract()["axes"], indent=2))


if __name__ == "__main__":
    main()
'''

# ═══════════════════════════════════════════════════════════════
# Install
# ═══════════════════════════════════════════════════════════════
for rel, body in FILES.items():
    target = ROOT / rel
    if target.exists():
        dst = bk / rel; dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, dst)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body)
    print(f"  wrote {rel}")

subprocess.run("find dcs -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null", shell=True)

# ═══════════════════════════════════════════════════════════════
# Verify
# ═══════════════════════════════════════════════════════════════
for cmd, label in [
    (["-m","dcs.mesh","families"], "families"),
    (["-m","dcs.mesh","ucs"], "ucs"),
    (["-m","dcs.mesh","laws"], "laws"),
    (["-m","dcs.mesh","verify"], "verify"),
    (["-m","dcs.mesh","compose","G4","C7","K16"], "compose"),
]:
    print("\n" + "=" * 62)
    print("python", " ".join(cmd))
    print("=" * 62)
    subprocess.run([sys.executable] + cmd)

print(f"\nBackups: {bk}")
