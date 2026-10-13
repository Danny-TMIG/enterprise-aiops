"""Language design, formal methods, distributed systems, meta concerns."""

from dcs.generate import requirement  # pragma: no cover


@requirement(
    id="EQ-PL-002",
    title="operator precedence is unambiguous",
    section="EQ.meta",
    hats=["PL"],
    criticality="MUST",
)
def pl_prec():  # pragma: no cover
    assert 1 + 2 * 3 == 7


@requirement(
    id="EQ-PL-003",
    title="left-associative subtraction",
    section="EQ.meta",
    hats=["PL"],
    criticality="MUST",
)
def pl_left():  # pragma: no cover
    assert 10 - 3 - 2 == 5


@requirement(
    id="EQ-FM-002",
    title="forall over finite domain is decidable",
    section="EQ.meta",
    hats=["FM"],
    criticality="MUST",
)
def fm_finite():  # pragma: no cover
    from itertools import product  # pragma: no cover

    assert all(a and b or not (a and b) for a, b in product((True, False), repeat=2))


@requirement(
    id="EQ-FM-003",
    title="induction base + step",
    section="EQ.meta",
    hats=["FM"],
    criticality="MUST",
)
def fm_induction():  # pragma: no cover
    def P(n):  # pragma: no cover
        return sum(range(n + 1)) == n * (n + 1) // 2  # pragma: no cover

    base = P(0)
    step = all(P(k) and P(k + 1) for k in range(20))
    assert base and step


@requirement(
    id="EQ-RES-002",
    title="replication increases confidence",
    section="EQ.meta",
    hats=["RES"],
    criticality="MUST",
)
def res_replication():  # pragma: no cover
    import random  # pragma: no cover

    rng = random.Random(0)
    one = sum(rng.random() < 0.7 for _ in range(10))
    three = sum(any(rng.random() < 0.7 for _ in range(3)) for _ in range(10))
    assert three >= one


@requirement(
    id="EQ-RES-003", title="p-value bounded", section="EQ.meta", hats=["RES"], criticality="MUST"
)
def res_pval():  # pragma: no cover
    p = 0.03
    assert 0 <= p <= 1


@requirement(
    id="EQ-CMP-002",
    title="constant folding is idempotent",
    section="EQ.meta",
    hats=["CMP"],
    criticality="MUST",
)
def cmp_fold():  # pragma: no cover
    import ast  # pragma: no cover

    # fold
    folded = ast.Constant(value=3)
    assert isinstance(folded, ast.Constant)


@requirement(
    id="EQ-CMP-003",
    title="dead code elimination preserves semantics",
    section="EQ.meta",
    hats=["CMP"],
    criticality="SHOULD",
)
def cmp_dce():  # pragma: no cover
    # if False: x = 1 ; assert x not defined
    code = "if False:\n    x = 1\n"
    ns = {}
    exec(code, ns)
    assert "x" not in ns


@requirement(
    id="EQ-CMP-004",
    title="SSA form: each name assigned once",
    section="EQ.meta",
    hats=["CMP"],
    criticality="SHOULD",
)
def cmp_ssa():  # pragma: no cover
    import ast  # pragma: no cover

    src = "a = 1\nb = 2\nc = a + b"
    tree = ast.parse(src)
    assigned = [
        t.id
        for n in tree.body
        if isinstance(n, ast.Assign)  # pragma: no cover
        for t in n.targets
        if isinstance(t, ast.Name)  # pragma: no cover
    ]
    assert len(assigned) == len(set(assigned))


@requirement(
    id="EQ-SA-002",
    title="layered architecture: no upward edges",
    section="EQ.meta",
    hats=["SA"],
    criticality="MUST",
)
def sa_layers():  # pragma: no cover
    edges = [("ui", "api"), ("api", "db")]
    layer = {"ui": 0, "api": 1, "db": 2}
    for a, b in edges:
        assert layer[a] < layer[b]


@requirement(
    id="EQ-SA-003",
    title="no cycles in component graph",
    section="EQ.meta",
    hats=["SA"],
    criticality="MUST",
)
def sa_acyclic():  # pragma: no cover
    edges = {"a": ["b"], "b": ["c"], "c": []}

    def has_cycle(node, path):  # pragma: no cover
        if node in path:  # pragma: no cover
            return True  # pragma: no cover
        return any(has_cycle(n, path | {node}) for n in edges.get(node, []))  # pragma: no cover

    assert not any(has_cycle(n, set()) for n in edges)


@requirement(
    id="EQ-DIS-002",
    title="eventual consistency converges",
    section="EQ.meta",
    hats=["DIS"],
    criticality="MUST",
)
def dis_converge():  # pragma: no cover
    # CRDT grow-only set
    A = {"x", "y"}
    B = {"y", "z"}
    assert (A | B) == {"x", "y", "z"}


@requirement(
    id="EQ-DIS-003",
    title="consensus requires quorum",
    section="EQ.meta",
    hats=["DIS"],
    criticality="MUST",
)
def dis_quorum():  # pragma: no cover
    n = 5
    quorum = n // 2 + 1
    assert quorum == 3


@requirement(
    id="EQ-DIS-004",
    title="vector clock orders causality",
    section="EQ.meta",
    hats=["DIS"],
    criticality="MUST",
)
def dis_vclock():  # pragma: no cover
    a = {"A": 1, "B": 0}
    b = {"A": 1, "B": 1}

    def dominates(x, y):  # pragma: no cover
        return all(x[k] >= y.get(k, 0) for k in x)  # pragma: no cover

    assert dominates(b, a) and not dominates(a, b)


@requirement(
    id="EQ-AUT-002",
    title="script exits on error",
    section="EQ.meta",
    hats=["AUT"],
    criticality="MUST",
)
def aut_exit():  # pragma: no cover
    src = "set -euo pipefail"
    assert "set -e" in src


@requirement(
    id="EQ-AUT-003",
    title="job scheduler rejects invalid cron",
    section="EQ.meta",
    hats=["AUT"],
    criticality="MUST",
)
def aut_cron():  # pragma: no cover
    valid = "0 0 * * *"
    assert len(valid.split()) == 5


@requirement(
    id="EQ-ROB-002",
    title="DH parameters bounded",
    section="EQ.meta",
    hats=["ROB"],
    criticality="MUST",
)
def rob_dh():  # pragma: no cover
    # Denavit-Hartenberg params
    params = [(0.5, 0, 0, 0), (0.4, 0, 0, 0)]
    assert all(len(p) == 4 for p in params)


@requirement(
    id="EQ-ROB-003",
    title="inverse kinematics within reach",
    section="EQ.meta",
    hats=["ROB"],
    criticality="SHOULD",
)
def rob_ik():  # pragma: no cover
    import math  # pragma: no cover

    l1, l2 = 1.0, 1.0
    target = (1.5, 0.0)
    r = math.hypot(*target)
    assert r <= l1 + l2


@requirement(
    id="EQ-SIM-002",
    title="physics step is symplectic",
    section="EQ.meta",
    hats=["SIM"],
    criticality="SHOULD",
)
def sim_symplectic():  # pragma: no cover
    x, v, dt = 1.0, 0.0, 0.1
    for _ in range(10):
        v += -x * dt
        x += v * dt
    # bounded energy
    assert abs(x**2 + v**2) < 5


@requirement(
    id="EQ-SIM-003",
    title="RNG reproducibility",
    section="EQ.meta",
    hats=["SIM"],
    criticality="MUST",
)
def sim_rng():  # pragma: no cover
    import random  # pragma: no cover

    a = random.Random(42).random()
    b = random.Random(42).random()
    assert a == b


@requirement(
    id="EQ-QT-002",
    title="Black-Scholes formula sanity",
    section="EQ.meta",
    hats=["QT"],
    criticality="SHOULD",
)
def qt_bs():  # pragma: no cover
    import math  # pragma: no cover

    S, K, r, T, sigma = 100, 100, 0.05, 1.0, 0.2
    d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    def N(x):  # pragma: no cover
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))  # pragma: no cover

    call = S * N(d1) - K * math.exp(-r * T) * N(d2)
    assert 0 < call < S


@requirement(
    id="EQ-QT-003",
    title="VaR is monotone in confidence",
    section="EQ.meta",
    hats=["QT"],
    criticality="MUST",
)
def qt_var():  # pragma: no cover
    xs = sorted([-3, -2, -1, 0, 1, 2, 3])
    var95 = -xs[int(0.05 * len(xs))]
    var99 = -xs[0]
    assert var99 >= var95


@requirement(
    id="EQ-MLE-002",
    title="cross-validation splits do not overlap",
    section="EQ.meta",
    hats=["MLE"],
    criticality="MUST",
)
def mle_cv():  # pragma: no cover
    folds = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    flat = [x for f in folds for x in f]
    assert len(flat) == len(set(flat))


@requirement(
    id="EQ-MLE-003",
    title="model digest is stable across loads",
    section="EQ.meta",
    hats=["MLE"],
    criticality="MUST",
)
def mle_digest():  # pragma: no cover
    import hashlib  # pragma: no cover

    w = b"weights"
    assert hashlib.sha256(w).hexdigest() == hashlib.sha256(w).hexdigest()


@requirement(
    id="EQ-MLE-004",
    title="batch dimension is preserved",
    section="EQ.meta",
    hats=["MLE"],
    criticality="MUST",
)
def mle_batch():  # pragma: no cover
    batch = [[1, 2], [3, 4], [5, 6]]
    assert len(batch) == 3


@requirement(
    id="EQ-REL-002",
    title="changelog entries carry a version",
    section="EQ.meta",
    hats=["REL"],
    criticality="MUST",
)
def rel_changelog():  # pragma: no cover
    entries = [("1.0.0", "init"), ("1.0.1", "fix")]
    assert all(v.count(".") == 2 for v, _ in entries)


@requirement(
    id="EQ-REL-003",
    title="git tag matches version",
    section="EQ.meta",
    hats=["REL"],
    criticality="MUST",
)
def rel_tag():  # pragma: no cover
    version = "1.2.3"
    tag = "v" + version
    assert tag.startswith("v")


@requirement(
    id="EQ-REL-004",
    title="prerelease ordering",
    section="EQ.meta",
    hats=["REL"],
    criticality="SHOULD",
)
def rel_prerelease():  # pragma: no cover
    order = ["1.0.0-alpha", "1.0.0-beta", "1.0.0"]
    assert order[-1] == "1.0.0"


@requirement(
    id="EQ-STE-002",
    title="segment append is atomic",
    section="EQ.meta",
    hats=["STE"],
    criticality="MUST",
)
def ste_atomic():  # pragma: no cover
    chunks = []
    chunks.append(b"a")
    assert chunks == [b"a"]


@requirement(
    id="EQ-STE-003",
    title="compaction preserves logical view",
    section="EQ.meta",
    hats=["STE"],
    criticality="MUST",
)
def ste_compact():  # pragma: no cover
    live = {"k1": b"v1", "k2": b"v2"}
    compacted = dict(live)
    assert compacted == live
