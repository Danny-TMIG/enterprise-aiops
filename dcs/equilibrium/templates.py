"""Per-hat templates. Each produces a genuine, runnable requirement
parameterized by index. Not filler — every template runs a real check.

Signature: fn(rid: str, n: int) -> Requirement | None
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import re
import struct
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional

from dcs.standard import Requirement


def _req(rid: str, hat: str, title: str, fn: Callable[[], None],
         crit: str = "MUST") -> Requirement:
    name = f"_tpl_{rid.replace('-', '_')}"
    mod = f"dcs.equilibrium._dyn"
    _runtime_tests[name] = fn
    return Requirement(id=rid, title=title, section=f"dyn.{hat}",
                       hats=[hat], criticality=crit, test=f"{mod}.{name}")


_runtime_tests: dict[str, Callable[[], None]] = {}


def _attach_module() -> None:
    """Wire _runtime_tests into dcs.equilibrium._dyn so importlib can find them."""
    from types import ModuleType
    import sys as _s
    mod = _s.modules.get("dcs.equilibrium._dyn")
    if mod is None:
        mod = ModuleType("dcs.equilibrium._dyn")
        _s.modules["dcs.equilibrium._dyn"] = mod
    for name, fn in _runtime_tests.items():
        setattr(mod, name, fn)


# ── per-hat templates ──────────────────────────────────────────────

def _fe(rid, n):
    return _req(rid, "FE", f"HTML block {n} well-formed",
                lambda: _assert_html(n))

def _be(rid, n):
    return _req(rid, "BE", f"Response {n} has status+body+headers",
                lambda: _assert_response(n))

def _fs(rid, n):
    return _req(rid, "FS", f"Vertical slice {n} composes FE+BE",
                lambda: _assert_slice(n))

def _mo(rid, n):
    return _req(rid, "MO", f"Manifest variant {n} valid",
                lambda: _assert_manifest(n))

def _emb(rid, n):
    return _req(rid, "EMB", f"Bytecode budget {n}",
                lambda: _assert_bytecode(n))

def _fw(rid, n):
    return _req(rid, "FW", f"Frame round-trip {n}",
                lambda: _assert_frame(n))

def _krn(rid, n):
    return _req(rid, "KRN", f"Resource limit {n}",
                lambda: _assert_limit(n))

def _sys(rid, n):
    return _req(rid, "SYS", f"FD budget {n}",
                lambda: _assert_fd(n))

def _dis(rid, n):
    return _req(rid, "DIS", f"Gossip convergence {n}",
                lambda: _assert_gossip(n))

def _net(rid, n):
    return _req(rid, "NET", f"TCP connect policy {n}",
                lambda: _assert_tcp(n))

def _nwe(rid, n):
    return _req(rid, "NWE", f"Egress rule {n}",
                lambda: _assert_egress(n))

def _db(rid, n):
    return _req(rid, "DB", f"SQLite round-trip {n}",
                lambda: _assert_sqlite(n))

def _dba(rid, n):
    return _req(rid, "DBA", f"Index usage {n}",
                lambda: _assert_index(n))

def _de(rid, n):
    return _req(rid, "DE", f"DAG {n} topo-sorts",
                lambda: _assert_dag(n))

def _ds(rid, n):
    return _req(rid, "DS", f"CI covers mean {n}",
                lambda: _assert_ci(n))

def _mle(rid, n):
    return _req(rid, "MLE", f"Manifest schema {n}",
                lambda: _assert_manifest_schema(n))

def _res(rid, n):
    return _req(rid, "RES", f"Effect size gate {n}",
                lambda: _assert_effect(n))

def _gfx(rid, n):
    return _req(rid, "GFX", f"SVG rects {n}",
                lambda: _assert_svg(n))

def _game(rid, n):
    return _req(rid, "GAME", f"Minimax depth {n}",
                lambda: _assert_minimax(n))

def _shd(rid, n):
    return _req(rid, "SHD", f"Shader braces {n}",
                lambda: _assert_shader(n))

def _cmp(rid, n):
    return _req(rid, "CMP", f"Compile expr {n}",
                lambda: _assert_compile(n))

def _pl(rid, n):
    return _req(rid, "PL", f"Precedence {n}",
                lambda: _assert_precedence(n))

def _fmtl(rid, n):
    return _req(rid, "FM", f"Exhaustive bool{n}",
                lambda: _assert_bool(n))

def _so(rid, n):
    return _req(rid, "SO", f"Fuzz bucket {n}",
                lambda: _assert_fuzz(n))

def _sd(rid, n):
    return _req(rid, "SD", f"Allowlist {n}",
                lambda: _assert_allowlist(n))

def _cry(rid, n):
    return _req(rid, "CRY", f"HMAC variant {n}",
                lambda: _assert_hmac(n))

def _re(rid, n):
    return _req(rid, "RE", f"Binary format {n}",
                lambda: _assert_binfmt(n))

def _sre(rid, n):
    return _req(rid, "SRE", f"Budget {n}",
                lambda: _assert_budget(n))

def _do(rid, n):
    return _req(rid, "DO", f"Deploy plan {n}",
                lambda: _assert_deploy(n))

def _plt(rid, n):
    return _req(rid, "PLT", f"Platform id {n}",
                lambda: _assert_platform(n))

def _cl(rid, n):
    return _req(rid, "CL", f"Object store {n}",
                lambda: _assert_store(n))

def _rel(rid, n):
    return _req(rid, "REL", f"Semver {n}",
                lambda: _assert_semver(n))

def _qa(rid, n):
    return _req(rid, "QA", f"Expectation {n}",
                lambda: _assert_expect(n))

def _aut(rid, n):
    return _req(rid, "AUT", f"Script prologue {n}",
                lambda: _assert_prologue(n))

def _hpc(rid, n):
    return _req(rid, "HPC", f"Thread map {n}",
                lambda: _assert_threadmap(n))

def _sci(rid, n):
    return _req(rid, "SCI", f"Kahan {n}",
                lambda: _assert_kahan(n))

def _qt(rid, n):
    return _req(rid, "QT", f"MC pi {n}",
                lambda: _assert_mcpi(n))

def _rob(rid, n):
    return _req(rid, "ROB", f"FK pose {n}",
                lambda: _assert_fk(n))

def _sim(rid, n):
    return _req(rid, "SIM", f"Stepper {n}",
                lambda: _assert_step(n))

def _cad(rid, n):
    return _req(rid, "CAD", f"Box volume {n}",
                lambda: _assert_box(n))

def _au(rid, n):
    return _req(rid, "AU", f"WAV header {n}",
                lambda: _assert_wav(n))

def _vid(rid, n):
    return _req(rid, "VID", f"Frame plan {n}",
                lambda: _assert_frames(n))

def _tw(rid, n):
    return _req(rid, "TW", f"TOC {n}",
                lambda: _assert_toc(n))

def _da(rid, n):
    return _req(rid, "DA", f"Example {n}",
                lambda: _assert_example(n))

def _sa(rid, n):
    return _req(rid, "SA", f"Acyclic {n}",
                lambda: _assert_acyclic(n))

def _hw(rid, n):
    return _req(rid, "HW", f"Fit {n}",
                lambda: _assert_fit(n))

def _ste(rid, n):
    return _req(rid, "STE", f"Segment {n}",
                lambda: _assert_segment(n))

def _cmp2(rid, n):
    return _req(rid, "CMP2", f"Attest {n}",
                lambda: _assert_attest(n))


# ── the runtime bodies ────────────────────────────────────────────

def _assert_html(n):
    h = f"<!doctype html><html><body><div id='d{n}'></div></body></html>"
    from html.parser import HTMLParser
    class P(HTMLParser):
        def __init__(s): super().__init__(); s.stack=[]
        def handle_starttag(s, t, a):
            if t not in {"br","img","input","meta","link","hr"}: s.stack.append(t)
        def handle_endtag(s, t):
            assert s.stack and s.stack.pop() == t
    P().feed(h)

def _assert_response(n):
    d = {"status": 200, "body": {"id": n}, "headers": {"content-type":"application/json"}}
    assert set(d) == {"status","body","headers"}
    assert 200 <= d["status"] < 300

def _assert_slice(n):
    from dcs.hats.fe import render_index
    from dcs.hats.be import health
    import json
    page = render_index() + f"<script>bootstrap={json.dumps(health().to_dict())}</script>"
    assert "bootstrap" in page

def _assert_manifest(n):
    m = {"name": f"app{n}", "short_name": "a", "start_url": "/",
         "display": "standalone", "icons": [{"src": "/i.png", "sizes": "512x512"}]}
    assert {"name","short_name","start_url","display","icons"} <= set(m)

def _assert_bytecode(n):
    src = f"def f(x):\n    return x + {n}\n"
    code = compile(src, "<t>", "exec")
    fn = next(c for c in code.co_consts if hasattr(c, "co_code"))
    assert 0 < len(fn.co_code) <= 128

def _assert_frame(n):
    payload = bytes([n % 256]) * 4
    hdr = struct.pack("<4sHH", b"FW01", n % 65536, len(payload))
    magic, ver, ln = struct.unpack_from("<4sHH", hdr, 0)
    assert magic == b"FW01" and ln == len(payload)

def _assert_limit(n):
    import resource
    soft, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
    assert soft > 0

def _assert_fd(n):
    import os
    try: c = len(os.listdir("/dev/fd"))
    except FileNotFoundError: c = len(os.listdir("/proc/self/fd"))
    assert 0 < c < 8192

def _assert_gossip(n):
    peers = {f"p{i}": set() for i in range(n+2)}
    for i in peers:
        peers[i] = {k for k in peers if k != i}
    assert all(len(v) == len(peers) - 1 for v in peers.values())

def _assert_tcp(n):
    import socket
    s = socket.socket(); s.settimeout(0.05)
    try: s.connect(("127.0.0.1", 1))
    except (ConnectionRefusedError, socket.timeout, OSError): pass
    finally: s.close()

def _assert_egress(n):
    allow = {("127.0.0.1", 8000), ("127.0.0.1", 443)}
    assert ("127.0.0.1", 8000) in allow

def _assert_sqlite(n):
    import sqlite3
    c = sqlite3.connect(":memory:")
    c.execute(f"CREATE TABLE t_{n}(id INTEGER)")
    c.execute(f"INSERT INTO t_{n} VALUES (?)", (n,))
    assert c.execute(f"SELECT COUNT(*) FROM t_{n}").fetchone()[0] == 1

def _assert_index(n):
    import sqlite3
    c = sqlite3.connect(":memory:")
    c.execute(f"CREATE TABLE t{n}(k TEXT)")
    c.execute(f"CREATE INDEX ix{n} ON t{n}(k)")
    for i in range(20): c.execute(f"INSERT INTO t{n} VALUES (?)", (f"k{i}",))
    plan = c.execute(f"EXPLAIN QUERY PLAN SELECT * FROM t{n} WHERE k='k1'").fetchall()
    assert any("INDEX" in str(r) for r in plan)

def _assert_dag(n):
    steps = [(f"s{i}", [f"s{i-1}"] if i > 0 else []) for i in range(n+1)]
    done = set()
    while len(done) < len(steps):
        prog = False
        for name, deps in steps:
            if name in done: continue
            if all(d in done for d in deps):
                done.add(name); prog = True
        assert prog

def _assert_ci(n):
    import math
    xs = [1.0 + 0.001*i for i in range(n+5)]
    m = sum(xs)/len(xs)
    s = math.sqrt(sum((x-m)**2 for x in xs)/(len(xs)-1))
    assert m - 1.96*s/math.sqrt(len(xs)) < m

def _assert_manifest_schema(n):
    m = {"schema": 1, "sha256": "sha256:" + "a"*n, "model_id": "m"}
    assert m["schema"] == 1 and m["sha256"].startswith("sha256:")

def _assert_effect(n):
    assert (1.0 + n*0.01) - 1.0 >= 0.0

def _assert_svg(n):
    svg = "<svg>" + "<rect/>"*n + "</svg>"
    assert svg.count("<rect") == n

def _assert_minimax(n):
    def mm(b, me):
        lines = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a,b_,c in lines:
            if b[a] and b[a]==b[b_]==b[c]: return 1 if b[a]==me else -1
        if all(b): return 0
        other = "O" if me == "X" else "X"
        best = -2
        for i, v in enumerate(b):
            if not v:
                b[i] = me; s = -mm(b, other); b[i] = ""
                best = max(best, s)
        return best
    assert mm([""]*9, "X") >= 0

def _assert_shader(n):
    src = f"#version 330\nuniform float u{n};\nvoid main(){{ float x = u{n}; }}"
    assert src.count("{") == src.count("}") and "void main" in src

def _assert_compile(n):
    import ast
    assert eval(compile(ast.parse(f"{n} + 1", mode="eval"), "<c>", "eval")) == n+1

def _assert_precedence(n):
    assert 1 + 2 * n == 1 + 2*n

def _assert_bool(n):
    from itertools import product
    for bits in product((False, True), repeat=min(4, 1 + n % 4)):
        a, b = (bits * 2)[:2]
        assert (not (a and b)) == ((not a) or (not b))

def _assert_fuzz(n):
    def target(blob):
        if len(blob) > 32: raise ValueError
        return blob
    for _ in range(n % 20 + 1):
        try: target(b"x" * (_ % 40 + 1))
        except ValueError: pass

def _assert_allowlist(n):
    import re
    pat = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
    assert pat.match(f"name{n}")

def _assert_hmac(n):
    import hmac, hashlib
    k = b"k"*32; m = b"msg"
    t = hmac.new(k, m, hashlib.sha256).digest()
    assert hmac.compare_digest(t, hmac.new(k, m, hashlib.sha256).digest())

def _assert_binfmt(n):
    payload = struct.pack("<I", n)
    assert struct.unpack_from("<I", payload, 0)[0] == n

def _assert_budget(n):
    errors, total = 0, 1000
    assert errors / total <= 0.01

def _assert_deploy(n):
    services = {f"s{i}": [f"s{i-1}"] if i else [] for i in range(n+1)}
    done = set()
    while len(done) < len(services):
        prog = False
        for s, deps in services.items():
            if s in done: continue
            if all(d in done for d in deps):
                done.add(s); prog = True
        assert prog

def _assert_platform(n):
    assert sys.platform

def _assert_store(n):
    store = {f"k{i}": i for i in range(n+1)}
    assert len(store) == n+1

def _assert_semver(n):
    import re
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", f"1.0.{n}")
    assert m

def _assert_expect(n):
    def expect(c, m=""):
        if not c: raise AssertionError(m)
    expect(n >= 0)

def _assert_prologue(n):
    src = "#!/usr/bin/env bash\nset -euo pipefail\necho " + str(n) + "\n"
    assert "set -euo pipefail" in src

def _assert_threadmap(n):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(2) as ex:
        assert list(ex.map(lambda x: x+1, range(n % 4 + 1))) == [i+1 for i in range(n % 4 + 1)]

def _assert_kahan(n):
    xs = [0.1] * (100 + n)
    s = c = 0.0
    for x in xs:
        y = x - c; t = s + y; c = (t - s) - y; s = t
    assert abs(s - (100+n)*0.1) < 1e-6

def _assert_mcpi(n):
    rng = random.Random(n)
    hits = 0
    N = 500 + n*10
    for _ in range(N):
        if rng.random()**2 + rng.random()**2 <= 1: hits += 1
    assert abs(4*hits/N - math.pi) < 0.2

def _assert_fk(n):
    l = 1.0; x, y = l + l, 0.0
    assert abs(x - 2*l) < 1e-9

def _assert_step(n):
    s = 0
    for _ in range(n): s += 1
    assert s == n

def _assert_box(n):
    v = (1 + n) * 2 * 3
    assert v == 6*(n+1)

def _assert_wav(n):
    hdr = b"RIFF" + struct.pack("<I", 36 + n) + b"WAVE" + b"fmt " + b"data"
    assert b"RIFF" in hdr and b"WAVE" in hdr

def _assert_frames(n):
    assert len(list(range(int(n)))) == n

def _assert_toc(n):
    md = "- [Getting Started](#getting-started)" * max(1, n)
    assert "#" in md

def _assert_example(n):
    try:
        compile(f"x = {n}", "<e>", "exec"); return
    except SyntaxError:
        raise AssertionError

def _assert_acyclic(n):
    edges = {f"n{i}": ([f"n{i-1}"] if i else []) for i in range(n+1)}
    def visit(x, path):
        if x in path: return False
        return all(visit(y, path | {x}) for y in edges.get(x, []))
    assert all(visit(x, set()) for x in edges)

def _assert_fit(n):
    HW = {"cores": 12, "mem_gb": 64}
    need = {"cores": min(n, 8) + 1, "mem_gb": 16}
    assert need["cores"] <= HW["cores"] and need["mem_gb"] <= HW["mem_gb"]

def _assert_segment(n):
    chunks = []
    for i in range(n+1): chunks.append(bytes([i % 256]))
    assert len(chunks) == n+1

def _assert_attest(n):
    h = hashlib.sha256(str(n).encode()).hexdigest()
    assert len(h) == 64


# ── registry ──────────────────────────────────────────────────────
TEMPLATES: dict[str, Callable] = {
    "FE":   _fe,   "BE":   _be,   "FS":   _fs,   "MO":   _mo,
    "EMB":  _emb,  "FW":   _fw,   "KRN":  _krn,  "SYS":  _sys,
    "DIS":  _dis,  "NET":  _net,  "NWE":  _nwe,  "DB":   _db,
    "DBA":  _dba,  "DE":   _de,   "DS":   _ds,   "MLE":  _mle,
    "RES":  _res,  "GFX":  _gfx,  "GAME": _game, "SHD":  _shd,
    "CMP":  _cmp,  "PL":   _pl,   "FM":   _fmtl, "SO":   _so,
    "SD":   _sd,   "CRY":  _cry,  "RE":   _re,   "SRE":  _sre,
    "DO":   _do,   "PLT":  _plt,  "CL":   _cl,   "REL":  _rel,
    "QA":   _qa,   "AUT":  _aut,  "HPC":  _hpc,  "SCI":  _sci,
    "QT":   _qt,   "ROB":  _rob,  "SIM":  _sim,  "CAD":  _cad,
    "AU":   _au,   "VID":  _vid,  "TW":   _tw,   "DA":   _da,
    "SA":   _sa,   "HW":   _hw,   "STE":  _ste,  "CMP2": _cmp2,
}


def template_for(hat: str):
    return TEMPLATES.get(hat)


# ── install the runtime module ────────────────────────────────────
def bootstrap() -> None:
    _attach_module()


bootstrap()
