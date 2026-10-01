"""The DevSkills signature.

Only what the corrected list contains: languages/runtimes and
core-CS algorithms (plus a representative slice of each downstream
domain the list names). Nothing philosophical. Nothing invented.
"""

LANGS = [
    "python", "c", "cpp", "rust", "julia", "fortran",
    "cuda-c", "opencl-c", "sycl", "hip",
    "verilog", "systemverilog", "vhdl", "chisel", "spinalhdl", "amaranth",
    "qsharp", "openqasm",
    "lean", "coq", "isabelle-hol", "agda", "idris",
    "sql", "graphql", "protobuf", "flatbuffers", "capnproto",
    "typescript", "javascript", "wasm",
    "bash", "powershell",
]

ALGOS = [
    # data structures
    "array", "hash-map", "b-tree", "lsm-tree", "heap", "graph", "dag",
    "union-find", "segment-tree", "fenwick-tree", "trie", "suffix-array",
    "bloom-filter", "hyperloglog", "count-min-sketch", "merkle-tree",
    "crdt", "vector-clock",
    # search / graph
    "sorting", "searching", "graph-traversal",
    "dijkstra", "a-star", "bellman-ford", "floyd-warshall",
    "max-flow", "min-cut", "matching",
    # optimization
    "lp", "milp", "convex-optimization", "nonconvex-optimization",
    "gradient-descent", "adam", "l-bfgs", "cma-es",
    "bayesian-optimization", "mcts", "simulated-annealing",
    "genetic-algorithms",
    # paradigms
    "dynamic-programming", "divide-and-conquer", "greedy",
    "backtracking", "branch-and-bound", "constraint-satisfaction",
    "sat", "smt",
    # linear algebra / signal
    "linear-algebra", "matrix-decomposition", "sparse-linear-algebra",
    "eigenvalue-solver", "fft", "convolution", "correlation",
    "signal-filtering",
    # numerical solvers
    "fdm", "fem", "fvm", "sem", "dg", "spectral-methods",
    "multigrid", "amg", "krylov", "cg", "gmres", "bicgstab",
    "preconditioner", "runge-kutta", "cfl", "adjoint", "sensitivity",
    "uq", "polynomial-chaos", "surrogate-modeling",
    "monte-carlo", "molecular-dynamics", "dft", "tddft",
    "coupled-cluster", "qmc", "dmrg", "tensor-network",
    # ML
    "transformer", "attention", "flashattention", "ssm", "mamba",
    "gnn", "gat", "equivariant-network", "se3", "e3",
    "pinn", "neural-operator", "fno", "deeponet",
    "rl", "ppo", "sac", "td3", "ddpg", "dqn", "rainbow", "impala", "a3c",
    "alphazero", "muzero",
    "gan", "vae", "normalizing-flow", "diffusion", "score-based",
    "rlhf", "dpo", "constitutional-ai",
    "sparse-autoencoder", "activation-steering", "red-teaming",
    # quantum
    "shor", "grover", "hhl", "qft", "amplitude-amplification",
    "vqe", "qaoa", "quantum-annealing", "quantum-walk",
    "surface-code", "toric-code", "color-code", "lattice-surgery",
    "magic-state-distillation", "mwpm", "belief-propagation",
    # control
    "pid", "lqr", "lqg", "h-infinity", "mpc",
    "robust-control", "adaptive-control", "sliding-mode",
    "backstepping", "lyapunov", "observer",
    "kalman", "ekf", "ukf", "particle-filter",
    # robotics
    "slam", "icp", "ndt", "ransac", "teaser", "factor-graph",
    "bundle-adjustment", "a-star-robotics", "d-star", "rrt", "rrt-star",
    "prm", "chomp", "stomp", "trajopt", "whole-body-control",
    "contact-dynamics", "differentiable-physics", "sim2real",
    "domain-randomization",
    # formal
    "smt-z3", "cvc5", "yices", "model-checking", "nusmv", "spin",
    "prism", "storm", "theorem-proving", "type-theory",
    "category-theory", "hott",
]

DEV_SKILLS = {
    "languages": LANGS,
    "algorithms": ALGOS,
}

SIGNATURE = {
    "name": "DevSkills",
    "languages": LANGS,
    "algorithms": ALGOS,
    "count": len(LANGS) + len(ALGOS),
}
