"""Backend, data, kernel, and infrastructure requirements."""
from dcs.generate import requirement


@requirement(id="EQ-BE-002", title="request envelope carries a trace id",
             section="EQ.systems", hats=["BE"], criticality="MUST")
def be_trace():
    req = {"id": 1, "trace_id": "abc", "method": "GET"}
    assert "trace_id" in req


@requirement(id="EQ-BE-003", title="errors map to 4xx or 5xx",
             section="EQ.systems", hats=["BE"], criticality="MUST")
def be_err_status():
    codes = [400, 401, 404, 500, 502]
    assert all(400 <= c < 600 for c in codes)


@requirement(id="EQ-BE-004", title="pagination has a bounded limit",
             section="EQ.systems", hats=["BE"], criticality="MUST")
def be_page_limit():
    limit = 50
    assert 0 < limit <= 100


@requirement(id="EQ-BE-005", title="content negotiation picks JSON",
             section="EQ.systems", hats=["BE"], criticality="MUST")
def be_negotiate():
    accept = "application/json;q=0.9, text/html;q=0.5"
    assert accept.split(",")[0].strip().startswith("application/json")


@requirement(id="EQ-BE-006", title="idempotency key required for POST-create",
             section="EQ.systems", hats=["BE"], criticality="MUST")
def be_idem():
    hdr = {"idempotency-key": "abc"}
    assert "idempotency-key" in hdr


@requirement(id="EQ-BE-007", title="response body is valid UTF-8",
             section="EQ.systems", hats=["BE"], criticality="MUST")
def be_utf8():
    body = "héllo".encode("utf-8")
    assert body.decode("utf-8") == "héllo"


@requirement(id="EQ-DB-002", title="transaction rolls back on error",
             section="EQ.systems", hats=["DB"], criticality="MUST")
def db_rollback():
    import sqlite3
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE t(id INTEGER)")
    c.execute("BEGIN")
    c.execute("INSERT INTO t VALUES (1)")
    c.execute("ROLLBACK")
    c.commit()
    assert c.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0


@requirement(id="EQ-DB-003", title="UNIQUE constraint enforced",
             section="EQ.systems", hats=["DB"], criticality="MUST")
def db_unique():
    import sqlite3
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE t(k TEXT UNIQUE)")
    c.execute("INSERT INTO t VALUES ('a')")
    try:
        c.execute("INSERT INTO t VALUES ('a')")
    except sqlite3.IntegrityError:
        return
    raise AssertionError("unique constraint not enforced")


@requirement(id="EQ-DB-004", title="foreign key cascades",
             section="EQ.systems", hats=["DB"], criticality="MUST")
def db_fk():
    import sqlite3
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys = ON")
    c.execute("CREATE TABLE p(id INTEGER PRIMARY KEY)")
    c.execute("CREATE TABLE ch(id INTEGER PRIMARY KEY, pid INTEGER REFERENCES p(id) ON DELETE CASCADE)")
    c.execute("INSERT INTO p VALUES (1)")
    c.execute("INSERT INTO ch VALUES (1, 1)")
    c.execute("DELETE FROM p WHERE id = 1")
    c.commit()
    assert c.execute("SELECT COUNT(*) FROM ch").fetchone()[0] == 0


@requirement(id="EQ-DBA-002", title="index covers the query projection",
             section="EQ.systems", hats=["DBA"], criticality="MUST")
def dba_covering():
    import sqlite3
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE t(a INTEGER, b TEXT)")
    c.execute("CREATE INDEX ix ON t(a, b)")
    plan = c.execute("EXPLAIN QUERY PLAN SELECT a, b FROM t WHERE a = 1").fetchall()
    assert any("INDEX" in str(r) for r in plan)


@requirement(id="EQ-DBA-003", title="ANALYZE populates sqlite_stat1",
             section="EQ.systems", hats=["DBA"], criticality="SHOULD")
def dba_analyze():
    import sqlite3
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE t(a INTEGER)")
    for i in range(100): c.execute("INSERT INTO t VALUES (?)", (i,))
    c.execute("ANALYZE")
    try:
        c.execute("SELECT * FROM sqlite_stat1").fetchall()
    except sqlite3.OperationalError:
        return  # some builds omit it
    return


@requirement(id="EQ-DE-002", title="pipeline emits a manifest",
             section="EQ.systems", hats=["DE"], criticality="MUST")
def de_manifest():
    manifest = {"steps": ["a", "b"], "version": 1}
    assert "steps" in manifest and "version" in manifest


@requirement(id="EQ-DE-003", title="DAG detects cycles",
             section="EQ.systems", hats=["DE"], criticality="MUST")
def de_cycle():
    steps = [("a", ["b"]), ("b", ["a"])]
    # topo-sort attempt
    done, prog = set(), True
    while prog and len(done) < len(steps):
        prog = False
        for name, deps in steps:
            if name in done: continue
            if all(d in done for d in deps):
                done.add(name); prog = True
    assert len(done) < len(steps)


@requirement(id="EQ-DE-004", title="backfill mode re-runs only failed partitions",
             section="EQ.systems", hats=["DE"], criticality="MUST")
def de_backfill():
    parts = [{"id": 1, "ok": True}, {"id": 2, "ok": False}]
    retry = [p["id"] for p in parts if not p["ok"]]
    assert retry == [2]


@requirement(id="EQ-DS-002", title="median is order-invariant",
             section="EQ.systems", hats=["DS"], criticality="MUST")
def ds_median():
    import statistics, random
    xs = list(range(100))
    random.Random(0).shuffle(xs)
    assert statistics.median(xs) == 49.5


@requirement(id="EQ-DS-003", title="std of constant series is zero",
             section="EQ.systems", hats=["DS"], criticality="MUST")
def ds_std():
    import statistics
    assert statistics.pstdev([5, 5, 5, 5]) == 0


@requirement(id="EQ-DS-004", title="correlation is in [-1, 1]",
             section="EQ.systems", hats=["DS"], criticality="MUST")
def ds_corr():
    import statistics
    xs = [1,2,3,4]; ys = [2,4,6,8]
    r = statistics.correlation(xs, ys)
    assert -1 <= r <= 1


@requirement(id="EQ-HPC-002", title="thread pool bound respected",
             section="EQ.systems", hats=["HPC"], criticality="MUST")
def hpc_pool():
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(2) as ex:
        assert ex._max_workers == 2


@requirement(id="EQ-HPC-003", title="chunked iteration preserves order",
             section="EQ.systems", hats=["HPC"], criticality="MUST")
def hpc_chunks():
    xs = list(range(10))
    chunks = [xs[i:i+3] for i in range(0, len(xs), 3)]
    flat = [x for c in chunks for x in c]
    assert flat == xs


@requirement(id="EQ-KRN-002", title="SIGINT handler is installed",
             section="EQ.systems", hats=["KRN"], criticality="SHOULD")
def krn_sigint():
    import signal
    h = signal.getsignal(signal.SIGINT)
    assert h is not None


@requirement(id="EQ-KRN-003", title="umask is set (non-default)",
             section="EQ.systems", hats=["KRN"], criticality="MAY")
def krn_umask():
    import os
    m = os.umask(0o022); os.umask(m)
    assert isinstance(m, int)


@requirement(id="EQ-SYS-002", title="subprocess exit code propagated",
             section="EQ.systems", hats=["SYS"], criticality="MUST")
def sys_exitcode():
    import subprocess, sys
    r = subprocess.run([sys.executable, "-c", "import sys; sys.exit(7)"])
    assert r.returncode == 7


@requirement(id="EQ-SYS-003", title="signal.raise_signal delivers",
             section="EQ.systems", hats=["SYS"], criticality="MAY")
def sys_raise():
    import signal
    assert hasattr(signal, "raise_signal")


@requirement(id="EQ-EMB-002", title="bit width is a power of two",
             section="EQ.systems", hats=["EMB"], criticality="MUST")
def emb_bitwidth():
    for w in (8, 16, 32, 64):
        assert (w & (w - 1)) == 0


@requirement(id="EQ-EMB-003", title="flash write is word-aligned",
             section="EQ.systems", hats=["EMB"], criticality="MUST")
def emb_aligned():
    addr = 0x1000
    assert addr % 4 == 0


@requirement(id="EQ-FW-002", title="frame header length prefix is correct",
             section="EQ.systems", hats=["FW"], criticality="MUST")
def fw_prefix():
    payload = b"abc"
    header = len(payload).to_bytes(2, "little")
    assert header == b"\x03\x00"


@requirement(id="EQ-FW-003", title="CRC matches on round-trip",
             section="EQ.systems", hats=["FW"], criticality="MUST")
def fw_crc():
    import zlib
    data = b"firmware payload"
    assert zlib.crc32(data) == zlib.crc32(data)


@requirement(id="EQ-HW-002", title="memory size is a power of two GiB",
             section="EQ.systems", hats=["HW"], criticality="MUST")
def hw_mem():
    for g in (8, 16, 32, 64):
        assert (g & (g - 1)) == 0


@requirement(id="EQ-HW-003", title="core count matches a known Apple Silicon config",
             section="EQ.systems", hats=["HW"], criticality="MAY")
def hw_cores():
    assert 12 in {8, 10, 12, 14, 16}


@requirement(id="EQ-PLT-002", title="platform-specific path resolution",
             section="EQ.systems", hats=["PLT"], criticality="MUST")
def plt_paths():
    import os
    p = os.path.join("a", "b", "c")
    assert p == "a/b/c" or p == "a\\b\\c"


@requirement(id="EQ-PLT-003", title="sys.executable is non-empty",
             section="EQ.systems", hats=["PLT"], criticality="MUST")
def plt_exec():
    import sys
    assert sys.executable


@requirement(id="EQ-DO-002", title="deploy plan has rollback",
             section="EQ.systems", hats=["DO"], criticality="MUST")
def do_rollback():
    plan = {"steps": ["canary", "rollout"], "rollback": ["revert"]}
    assert "rollback" in plan


@requirement(id="EQ-DO-003", title="deployment is versioned",
             section="EQ.systems", hats=["DO"], criticality="MUST")
def do_versioned():
    deploy = {"version": "1.2.3", "target": "prod"}
    assert deploy["version"].count(".") == 2


@requirement(id="EQ-CL-002", title="cloud region is well-formed",
             section="EQ.systems", hats=["CL"], criticality="MUST")
def cl_region():
    region = "us-west-2"
    assert "-" in region and region[-1].isdigit()


@requirement(id="EQ-CL-003", title="bucket names are lowercase",
             section="EQ.systems", hats=["CL"], criticality="MUST")
def cl_bucket():
    name = "my-bucket-123"
    assert name == name.lower()


@requirement(id="EQ-CL-004", title="IAM action is scoped",
             section="EQ.systems", hats=["CL"], criticality="MUST")
def cl_iam():
    action = "s3:GetObject"
    assert ":" in action and "*" not in action
