"""Six behavior families: Generator, Compiler, Resolver, Daemon, Binary, Kernel.

Each family is {stage_id: (title, (op, ...))}. Stages are the atoms of the
MESH pipeline algebra. Families are axes: which TRIAD axis a stage stresses.
"""

from __future__ import annotations  # pragma: no cover

_TAX = {
    "G": (
        "Generator",
        {
            "G0": ("Bootstrap", ("Initialize", "Discover", "Configure", "Provision", "Self-host")),
            "G1": ("Parse", ("Lex", "Tokenize", "Parse", "Normalize", "Canonicalize")),
            "G2": (
                "Analyze",
                (
                    "Type inference",
                    "Constraint analysis",
                    "Dependency analysis",
                    "Symbol resolution",
                    "Scope resolution",
                    "Semantic analysis",
                    "Data-flow analysis",
                    "Control-flow analysis",
                    "Graph analysis",
                ),
            ),
            "G3": (
                "Transform",
                (
                    "Rewrite",
                    "Expand",
                    "Reduce",
                    "Fold",
                    "Inline",
                    "Lift",
                    "Lower",
                    "Compose",
                    "Decompose",
                    "Optimize",
                    "Normalize",
                ),
            ),
            "G4": (
                "Synthesize",
                (
                    "Generate source code",
                    "Generate schemas",
                    "Generate registries",
                    "Generate APIs",
                    "Generate SDKs",
                    "Generate documentation",
                    "Generate tests",
                    "Generate benchmarks",
                    "Generate proofs",
                    "Generate examples",
                    "Generate configuration",
                    "Generate build scripts",
                ),
            ),
            "G5": (
                "Emit",
                (
                    "Write files",
                    "Write directories",
                    "Serialize",
                    "Stream",
                    "Package",
                    "Compress",
                    "Archive",
                ),
            ),
            "G6": (
                "Validate",
                (
                    "Syntax validation",
                    "Schema validation",
                    "Type validation",
                    "Constraint validation",
                    "Cross-reference validation",
                    "Dependency validation",
                    "Conformance validation",
                    "Completeness validation",
                ),
            ),
            "G7": (
                "Execute",
                (
                    "Invoke compiler",
                    "Invoke linker",
                    "Invoke formatter",
                    "Invoke linter",
                    "Invoke test runner",
                    "Invoke benchmark runner",
                    "Invoke packager",
                    "Invoke deployment",
                ),
            ),
            "G8": (
                "Coordinate",
                (
                    "Schedule",
                    "Queue",
                    "Pipeline",
                    "Parallelize",
                    "Synchronize",
                    "Retry",
                    "Resume",
                    "Checkpoint",
                ),
            ),
            "G9": (
                "Observe",
                ("Log", "Trace", "Profile", "Measure", "Benchmark", "Collect metrics", "Audit"),
            ),
            "G10": ("Persist", ("Cache", "Index", "Snapshot", "Version", "Store state", "Recover")),
            "G11": (
                "Publish",
                (
                    "Package",
                    "Sign",
                    "Generate SBOM",
                    "Generate manifest",
                    "Generate checksums",
                    "Attest",
                    "Release",
                    "Archive",
                ),
            ),
            "G12": (
                "Self-Evolve",
                (
                    "Generate generators",
                    "Regenerate repository",
                    "Regenerate IR",
                    "Regenerate schemas",
                    "Regenerate registries",
                    "Refactor generated code",
                    "Migrate versions",
                    "Self-verify",
                ),
            ),
        },
    ),
    "C": (
        "Compiler",
        {
            "C0": (
                "Bootstrap Compiler",
                (
                    "Initialize compilation",
                    "Load configuration",
                    "Load toolchain",
                    "Discover modules",
                    "Build dependency graph",
                    "Self-host",
                ),
            ),
            "C1": (
                "Front-End",
                (
                    "Read input",
                    "Decode",
                    "Lex",
                    "Tokenize",
                    "Parse",
                    "Build AST",
                    "Build CST",
                    "Build symbol tables",
                ),
            ),
            "C2": (
                "Semantic Compiler",
                (
                    "Name resolution",
                    "Namespace resolution",
                    "Scope resolution",
                    "Type checking",
                    "Type inference",
                    "Constraint solving",
                    "Attribute propagation",
                    "Generic instantiation",
                    "Constant evaluation",
                    "Semantic validation",
                ),
            ),
            "C3": (
                "Intermediate Representation",
                (
                    "Build IR",
                    "Normalize IR",
                    "Canonicalize IR",
                    "Annotate IR",
                    "Merge IR",
                    "Split IR",
                    "Lower IR",
                    "Raise IR",
                    "Serialize IR",
                ),
            ),
            "C4": (
                "Analysis",
                (
                    "Dependency analysis",
                    "Data-flow analysis",
                    "Control-flow analysis",
                    "Call graph construction",
                    "Dominator analysis",
                    "Alias analysis",
                    "Escape analysis",
                    "Liveness analysis",
                    "Reachability analysis",
                    "Dead-code analysis",
                ),
            ),
            "C5": (
                "Optimization",
                (
                    "Constant folding",
                    "Constant propagation",
                    "Copy propagation",
                    "Dead-code elimination",
                    "Common subexpression elimination",
                    "Loop optimization",
                    "Inlining",
                    "Outlining",
                    "Vectorization",
                    "Parallelization",
                    "Fusion",
                    "Fission",
                    "Scheduling",
                    "Register allocation",
                    "Memory optimization",
                ),
            ),
            "C6": (
                "Transformation",
                (
                    "Rewrite",
                    "Lower",
                    "Lift",
                    "Expand",
                    "Reduce",
                    "Compose",
                    "Decompose",
                    "Refactor",
                    "Specialize",
                    "Generalize",
                    "Transpile",
                ),
            ),
            "C7": (
                "Back-End",
                (
                    "Instruction selection",
                    "Code generation",
                    "Assembly generation",
                    "Object generation",
                    "Bytecode generation",
                    "WASM generation",
                    "LLVM IR generation",
                    "Machine code generation",
                ),
            ),
            "C8": (
                "Linking",
                (
                    "Static linking",
                    "Dynamic linking",
                    "Symbol resolution",
                    "Library resolution",
                    "Relocation",
                    "Binary layout",
                    "Packaging",
                ),
            ),
            "C9": (
                "Verification",
                (
                    "Syntax verification",
                    "Semantic verification",
                    "Type verification",
                    "Constraint verification",
                    "IR verification",
                    "Optimization verification",
                    "Binary verification",
                ),
            ),
            "C10": (
                "Artifact Generation",
                (
                    "Executables",
                    "Libraries",
                    "Modules",
                    "Packages",
                    "Containers",
                    "SDKs",
                    "APIs",
                    "Documentation",
                    "Debug symbols",
                    "Metadata",
                ),
            ),
            "C11": (
                "Runtime Preparation",
                (
                    "Loader generation",
                    "Startup generation",
                    "Initialization",
                    "Resource embedding",
                    "Configuration embedding",
                    "Reflection metadata",
                ),
            ),
            "C12": (
                "Incremental Compilation",
                (
                    "Cache",
                    "Dependency tracking",
                    "Dirty checking",
                    "Incremental rebuild",
                    "Partial recompilation",
                ),
            ),
            "C13": (
                "Distributed Compilation",
                (
                    "Task partitioning",
                    "Remote execution",
                    "Work stealing",
                    "Result aggregation",
                    "Fault recovery",
                ),
            ),
            "C14": (
                "Diagnostics",
                (
                    "Errors",
                    "Warnings",
                    "Notes",
                    "Suggestions",
                    "Trace output",
                    "Debug information",
                    "Profiling information",
                ),
            ),
            "C15": (
                "Publication",
                (
                    "Manifest generation",
                    "Checksums",
                    "Digital signatures",
                    "SBOM generation",
                    "Provenance metadata",
                    "Release packaging",
                ),
            ),
            "C16": (
                "Self-Hosting",
                (
                    "Compile compiler",
                    "Compile generators",
                    "Regenerate compiler",
                    "Cross-compile compiler",
                    "Bootstrap next compiler version",
                    "Verify compiler fixed point",
                ),
            ),
        },
    ),
    "R": (
        "Resolver",
        {
            "R0": (
                "Bootstrap Resolution",
                (
                    "Initialize resolver",
                    "Load environment",
                    "Load registries",
                    "Load namespaces",
                    "Load caches",
                    "Build resolution context",
                ),
            ),
            "R1": (
                "Identity Resolution",
                (
                    "Resolve identifier",
                    "Resolve UUID",
                    "Resolve canonical ID",
                    "Resolve aliases",
                    "Resolve symbols",
                    "Resolve handles",
                    "Resolve references",
                ),
            ),
            "R2": (
                "Namespace Resolution",
                (
                    "Resolve namespace",
                    "Resolve package",
                    "Resolve module",
                    "Resolve scope",
                    "Resolve ownership",
                    "Resolve visibility",
                    "Resolve imports",
                ),
            ),
            "R3": (
                "Type Resolution",
                (
                    "Resolve primitive types",
                    "Resolve composite types",
                    "Resolve generic types",
                    "Resolve tensor types",
                    "Resolve graph types",
                    "Resolve interfaces",
                    "Resolve inheritance",
                    "Resolve constraints",
                ),
            ),
            "R4": (
                "Symbol Resolution",
                (
                    "Resolve variables",
                    "Resolve functions",
                    "Resolve operators",
                    "Resolve constants",
                    "Resolve templates",
                    "Resolve overloads",
                    "Resolve polymorphism",
                ),
            ),
            "R5": (
                "Dependency Resolution",
                (
                    "Resolve direct dependencies",
                    "Resolve transitive dependencies",
                    "Resolve version constraints",
                    "Resolve conflicts",
                    "Resolve cycles",
                    "Resolve optional dependencies",
                    "Resolve platform dependencies",
                ),
            ),
            "R6": (
                "Constraint Resolution",
                (
                    "Solve constraints",
                    "Unify constraints",
                    "Propagate constraints",
                    "Detect contradictions",
                    "Detect satisfiability",
                    "Compute fixed points",
                ),
            ),
            "R7": (
                "Semantic Resolution",
                (
                    "Resolve meanings",
                    "Resolve definitions",
                    "Resolve requirements",
                    "Resolve invariants",
                    "Resolve semantics",
                    "Resolve contracts",
                    "Resolve obligations",
                ),
            ),
            "R8": (
                "Graph Resolution",
                (
                    "Resolve graph nodes",
                    "Resolve graph edges",
                    "Resolve paths",
                    "Resolve connectivity",
                    "Resolve hierarchy",
                    "Resolve topology",
                    "Resolve reachability",
                ),
            ),
            "R9": (
                "Reference Resolution",
                (
                    "Resolve hyperlinks",
                    "Resolve cross-references",
                    "Resolve traceability",
                    "Resolve citations",
                    "Resolve documentation links",
                    "Resolve registry references",
                ),
            ),
            "R10": (
                "Resource Resolution",
                (
                    "Resolve files",
                    "Resolve directories",
                    "Resolve URLs",
                    "Resolve APIs",
                    "Resolve services",
                    "Resolve databases",
                    "Resolve storage objects",
                ),
            ),
            "R11": (
                "Environment Resolution",
                (
                    "Resolve platform",
                    "Resolve architecture",
                    "Resolve toolchain",
                    "Resolve compiler",
                    "Resolve runtime",
                    "Resolve configuration",
                    "Resolve variables",
                ),
            ),
            "R12": (
                "Version Resolution",
                (
                    "Resolve semantic versions",
                    "Resolve compatibility",
                    "Resolve upgrade paths",
                    "Resolve downgrade paths",
                    "Resolve migrations",
                    "Resolve release channels",
                ),
            ),
            "R13": (
                "Execution Resolution",
                (
                    "Resolve execution order",
                    "Resolve scheduling",
                    "Resolve priorities",
                    "Resolve parallel tasks",
                    "Resolve synchronization",
                    "Resolve resource allocation",
                ),
            ),
            "R14": (
                "Conflict Resolution",
                (
                    "Detect ambiguity",
                    "Detect duplicates",
                    "Detect collisions",
                    "Resolve precedence",
                    "Resolve overrides",
                    "Resolve arbitration",
                ),
            ),
            "R15": (
                "Validation Resolution",
                (
                    "Resolve schema compliance",
                    "Resolve type compliance",
                    "Resolve registry compliance",
                    "Resolve constitutional compliance",
                    "Resolve conformance status",
                ),
            ),
            "R16": (
                "Publication Resolution",
                (
                    "Resolve artifacts",
                    "Resolve manifests",
                    "Resolve signatures",
                    "Resolve SBOM entries",
                    "Resolve provenance",
                    "Resolve archives",
                ),
            ),
            "R17": (
                "Self Resolution",
                (
                    "Resolve generator graph",
                    "Resolve compiler graph",
                    "Resolve bootstrap graph",
                    "Resolve fixed point",
                    "Resolve self-host dependencies",
                    "Resolve regeneration order",
                ),
            ),
        },
    ),
    "D": (
        "Daemon",
        {
            "D0": (
                "Bootstrap Daemon",
                (
                    "Initialize",
                    "Load configuration",
                    "Load state",
                    "Acquire locks",
                    "Discover services",
                    "Enter event loop",
                ),
            ),
            "D1": (
                "File System Daemon",
                (
                    "Watch files",
                    "Watch directories",
                    "Detect changes",
                    "Queue events",
                    "Debounce updates",
                    "Trigger rebuilds",
                ),
            ),
            "D2": (
                "Build Daemon",
                (
                    "Monitor build graph",
                    "Schedule builds",
                    "Execute build stages",
                    "Cache artifacts",
                    "Resume interrupted builds",
                    "Incremental rebuild",
                ),
            ),
            "D3": (
                "Registry Daemon",
                (
                    "Monitor registries",
                    "Validate entries",
                    "Detect conflicts",
                    "Synchronize registries",
                    "Publish updates",
                ),
            ),
            "D4": (
                "Dependency Daemon",
                (
                    "Monitor dependency graph",
                    "Detect additions",
                    "Detect removals",
                    "Resolve versions",
                    "Detect cycles",
                    "Refresh dependency cache",
                ),
            ),
            "D5": (
                "Compiler Daemon",
                (
                    "Accept compile requests",
                    "Maintain compiler cache",
                    "Incremental compilation",
                    "Cross-compilation",
                    "Worker management",
                ),
            ),
            "D6": (
                "Generator Daemon",
                (
                    "Watch Canonical IR",
                    "Generate artifacts",
                    "Regenerate outputs",
                    "Coordinate generators",
                    "Maintain generation state",
                ),
            ),
            "D7": (
                "Validation Daemon",
                (
                    "Run schema validation",
                    "Run semantic validation",
                    "Run registry validation",
                    "Run constitutional validation",
                    "Report violations",
                ),
            ),
            "D8": (
                "Conformance Daemon",
                (
                    "Execute test suites",
                    "Execute benchmarks",
                    "Measure coverage",
                    "Collect evidence",
                    "Produce reports",
                ),
            ),
            "D9": (
                "Runtime Daemon",
                (
                    "Launch workers",
                    "Manage processes",
                    "Restart failed workers",
                    "Monitor health",
                    "Manage resources",
                ),
            ),
            "D10": (
                "Scheduler Daemon",
                (
                    "Queue jobs",
                    "Prioritize jobs",
                    "Dispatch workers",
                    "Balance load",
                    "Retry failures",
                ),
            ),
            "D11": (
                "Cache Daemon",
                (
                    "Populate cache",
                    "Invalidate cache",
                    "Compact cache",
                    "Evict entries",
                    "Persist cache",
                ),
            ),
            "D12": (
                "Index Daemon",
                (
                    "Build indexes",
                    "Refresh indexes",
                    "Search indexes",
                    "Optimize indexes",
                    "Verify indexes",
                ),
            ),
            "D13": (
                "Logging Daemon",
                ("Collect logs", "Rotate logs", "Aggregate logs", "Filter logs", "Archive logs"),
            ),
            "D14": (
                "Metrics Daemon",
                (
                    "Collect metrics",
                    "Sample performance",
                    "Measure throughput",
                    "Measure latency",
                    "Export telemetry",
                ),
            ),
            "D15": (
                "Publication Daemon",
                (
                    "Package artifacts",
                    "Generate manifests",
                    "Generate checksums",
                    "Generate SBOM",
                    "Sign releases",
                    "Archive releases",
                ),
            ),
            "D16": (
                "Synchronization Daemon",
                (
                    "Replicate state",
                    "Synchronize repositories",
                    "Synchronize registries",
                    "Synchronize artifacts",
                    "Resolve divergence",
                ),
            ),
            "D17": (
                "Security Daemon",
                (
                    "Verify signatures",
                    "Verify integrity",
                    "Validate provenance",
                    "Detect tampering",
                    "Enforce policy",
                ),
            ),
            "D18": (
                "Orchestration Daemon",
                (
                    "Coordinate daemons",
                    "Maintain dependency order",
                    "Manage lifecycle",
                    "Recover failures",
                    "Graceful shutdown",
                    "Rolling restart",
                ),
            ),
            "D19": (
                "Self-Hosting Daemon",
                (
                    "Watch generator sources",
                    "Regenerate generators",
                    "Rebuild toolchain",
                    "Verify fixed point",
                    "Maintain self-hosting state",
                ),
            ),
        },
    ),
    "B": (
        "Binary",
        {
            "B0": (
                "Bootstrap Binary",
                (
                    "Entry point",
                    "Initialize runtime",
                    "Parse arguments",
                    "Load configuration",
                    "Discover environment",
                    "Dispatch execution",
                ),
            ),
            "B1": (
                "Executable Binary",
                (
                    "Native executable",
                    "PIE",
                    "Console application",
                    "GUI application",
                    "Service executable",
                    "Command-line tool",
                ),
            ),
            "B2": (
                "Object Binary",
                (
                    "Object file",
                    "Relocatable object",
                    "Static object",
                    "Intermediate object",
                    "Debug object",
                ),
            ),
            "B3": (
                "Library Binary",
                (
                    "Static library",
                    "Shared library",
                    "Dynamic library",
                    "Runtime library",
                    "Plugin library",
                ),
            ),
            "B4": (
                "Intermediate Binary",
                (
                    "Bytecode",
                    "Intermediate Representation",
                    "LLVM IR",
                    "WebAssembly",
                    "Virtual machine image",
                ),
            ),
            "B5": (
                "Loader Binary",
                (
                    "Program loader",
                    "Dynamic loader",
                    "Bootstrap loader",
                    "Module loader",
                    "Plugin loader",
                ),
            ),
            "B6": (
                "Linker Binary",
                ("Static linker", "Dynamic linker", "Incremental linker", "Cross linker"),
            ),
            "B7": (
                "Runtime Binary",
                (
                    "Runtime executable",
                    "Virtual machine",
                    "Interpreter",
                    "JIT runtime",
                    "AOT runtime",
                ),
            ),
            "B8": (
                "Service Binary",
                ("Daemon", "Worker", "Agent", "Coordinator", "Scheduler", "Dispatcher"),
            ),
            "B9": (
                "Generator Binary",
                (
                    "Code generator",
                    "Schema generator",
                    "Registry generator",
                    "IR generator",
                    "SDK generator",
                    "Documentation generator",
                ),
            ),
            "B10": (
                "Compiler Binary",
                (
                    "Front-end compiler",
                    "Optimizer",
                    "Back-end compiler",
                    "Cross compiler",
                    "Self-host compiler",
                ),
            ),
            "B11": (
                "Validation Binary",
                (
                    "Schema validator",
                    "Type validator",
                    "Registry validator",
                    "Conformance validator",
                    "Integrity validator",
                ),
            ),
            "B12": (
                "Packaging Binary",
                ("Packager", "Archiver", "Compressor", "Bundle creator", "Installer builder"),
            ),
            "B13": (
                "Deployment Binary",
                ("Publisher", "Deployer", "Installer", "Updater", "Provisioner"),
            ),
            "B14": (
                "Inspection Binary",
                (
                    "Disassembler",
                    "Binary analyzer",
                    "Symbol dumper",
                    "Metadata extractor",
                    "Dependency inspector",
                ),
            ),
            "B15": (
                "Security Binary",
                ("Signer", "Verifier", "Hasher", "Encryptor", "Decryptor", "Attestation generator"),
            ),
            "B16": (
                "Monitoring Binary",
                ("Logger", "Metrics collector", "Tracer", "Profiler", "Health checker"),
            ),
            "B17": (
                "Storage Binary",
                (
                    "Database engine",
                    "Cache engine",
                    "Index engine",
                    "Snapshot engine",
                    "Persistence engine",
                ),
            ),
            "B18": (
                "Network Binary",
                ("Client", "Server", "Proxy", "Gateway", "Relay", "Synchronizer"),
            ),
            "B19": (
                "Self-Hosting Binary",
                (
                    "Bootstrap compiler",
                    "Generator compiler",
                    "Repository compiler",
                    "Toolchain compiler",
                    "Binary reproducer",
                    "Fixed-point verifier",
                ),
            ),
        },
    ),
    "K": (
        "Kernel",
        {
            "K0": (
                "Bootstrap Kernel",
                (
                    "Initialize",
                    "Hardware discovery",
                    "Memory initialization",
                    "Interrupt initialization",
                    "Scheduler initialization",
                    "Runtime initialization",
                ),
            ),
            "K1": (
                "Process Kernel",
                (
                    "Create process",
                    "Destroy process",
                    "Suspend process",
                    "Resume process",
                    "Context switch",
                    "Process isolation",
                    "Process accounting",
                ),
            ),
            "K2": (
                "Thread Kernel",
                (
                    "Create thread",
                    "Destroy thread",
                    "Schedule thread",
                    "Synchronize thread",
                    "Join thread",
                    "Affinity management",
                ),
            ),
            "K3": (
                "Memory Kernel",
                (
                    "Allocate memory",
                    "Deallocate memory",
                    "Virtual memory",
                    "Physical memory",
                    "Paging",
                    "Mapping",
                    "Protection",
                    "Garbage collection",
                    "Memory compaction",
                ),
            ),
            "K4": (
                "Scheduling Kernel",
                (
                    "Priority scheduling",
                    "Fair scheduling",
                    "Real-time scheduling",
                    "Work stealing",
                    "Load balancing",
                    "Deadline scheduling",
                    "Queue management",
                ),
            ),
            "K5": (
                "Synchronization Kernel",
                (
                    "Mutexes",
                    "Semaphores",
                    "Read/write locks",
                    "Spinlocks",
                    "Barriers",
                    "Condition variables",
                    "Atomic operations",
                ),
            ),
            "K6": (
                "IPC Kernel",
                (
                    "Pipes",
                    "Queues",
                    "Shared memory",
                    "Signals",
                    "RPC",
                    "Message passing",
                    "Event dispatch",
                ),
            ),
            "K7": (
                "Filesystem Kernel",
                (
                    "Mount",
                    "Unmount",
                    "Read",
                    "Write",
                    "Cache",
                    "Journal",
                    "Permissions",
                    "Metadata management",
                ),
            ),
            "K8": (
                "Device Kernel",
                (
                    "Device discovery",
                    "Driver loading",
                    "Driver management",
                    "DMA",
                    "Interrupt routing",
                    "Device abstraction",
                ),
            ),
            "K9": (
                "Network Kernel",
                (
                    "Socket management",
                    "Packet routing",
                    "Transport protocols",
                    "Connection management",
                    "Congestion control",
                    "Firewall hooks",
                ),
            ),
            "K10": (
                "Security Kernel",
                (
                    "Authentication",
                    "Authorization",
                    "Access control",
                    "Capability management",
                    "Isolation",
                    "Auditing",
                    "Cryptographic interfaces",
                ),
            ),
            "K11": (
                "Resource Kernel",
                (
                    "CPU allocation",
                    "Memory allocation",
                    "I/O allocation",
                    "Storage allocation",
                    "Network allocation",
                    "Quota enforcement",
                ),
            ),
            "K12": (
                "Execution Kernel",
                (
                    "Instruction dispatch",
                    "Runtime execution",
                    "Exception handling",
                    "Trap handling",
                    "System calls",
                    "Fault recovery",
                ),
            ),
            "K13": (
                "Compiler Kernel",
                (
                    "Parse compilation units",
                    "Build IR",
                    "Optimize",
                    "Emit binaries",
                    "Incremental compilation",
                    "Cross compilation",
                ),
            ),
            "K14": (
                "Generator Kernel",
                (
                    "Execute generators",
                    "Schedule generators",
                    "Resolve generator dependencies",
                    "Stream generated artifacts",
                    "Incremental regeneration",
                    "Self-generation",
                ),
            ),
            "K15": (
                "Build Kernel",
                (
                    "Build graph execution",
                    "Dependency execution",
                    "Incremental builds",
                    "Artifact caching",
                    "Parallel execution",
                    "Build recovery",
                ),
            ),
            "K16": (
                "Conformance Kernel",
                (
                    "Execute validation graph",
                    "Execute test graph",
                    "Execute benchmark graph",
                    "Aggregate evidence",
                    "Produce certification state",
                ),
            ),
            "K17": (
                "Publication Kernel",
                (
                    "Package artifacts",
                    "Generate manifests",
                    "Generate SBOM",
                    "Generate signatures",
                    "Archive releases",
                    "Publish distributions",
                ),
            ),
            "K18": (
                "Orchestration Kernel",
                (
                    "Coordinate subsystems",
                    "Lifecycle management",
                    "Event routing",
                    "State management",
                    "Failure recovery",
                    "Distributed coordination",
                ),
            ),
            "K19": (
                "Self-Hosting Kernel",
                (
                    "Rebuild kernel",
                    "Rebuild toolchain",
                    "Rebuild generators",
                    "Verify fixed point",
                    "Maintain self-hosting invariants",
                    "Bootstrap successor kernel",
                ),
            ),
        },
    ),
}

AXIS_OF = {
    "G": "conformance",
    "C": "conformance",
    "R": "coherence",
    "D": "coordination",
    "B": "conformance",
    "K": "all",
}

FAMILIES = {
    fam: {
        "title": title,
        "stages": {sid: {"title": t, "ops": list(ops)} for sid, (t, ops) in stages.items()},
    }
    for fam, (title, stages) in _TAX.items()
}


def stage(sid: str) -> dict:  # pragma: no cover
    """Look up a stage by id, e.g. stage('G4')."""
    fam = sid[0]
    if fam not in _TAX or sid not in _TAX[fam][1]:  # pragma: no cover
        raise KeyError(f"unknown stage {sid!r}")  # pragma: no cover
    t, ops = _TAX[fam][1][sid]
    return {  # pragma: no cover
        "id": sid,
        "family": fam,
        "family_title": _TAX[fam][0],
        "title": t,
        "ops": list(ops),
        "axis": AXIS_OF[fam],
    }


def stages_of(fam: str):  # pragma: no cover
    return list(_TAX[fam][1])  # pragma: no cover
