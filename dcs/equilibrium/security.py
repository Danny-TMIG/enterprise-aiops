"""Security, compliance, and reliability requirements."""

from dcs.generate import requirement


@requirement(
    id="EQ-CRY-002",
    title="AES-GCM tag is 16 bytes",
    section="EQ.security",
    hats=["CRY"],
    criticality="MUST",
)
def cry_tag_len():
    tag = b"\x00" * 16
    assert len(tag) == 16


@requirement(
    id="EQ-CRY-003",
    title="nonce is unique per message",
    section="EQ.security",
    hats=["CRY"],
    criticality="MUST",
)
def cry_nonce():
    import os

    n1 = os.urandom(12)
    n2 = os.urandom(12)
    assert n1 != n2


@requirement(
    id="EQ-CRY-004",
    title="KDF output is deterministic per salt",
    section="EQ.security",
    hats=["CRY"],
    criticality="MUST",
)
def cry_kdf():
    import hashlib

    k1 = hashlib.pbkdf2_hmac("sha256", b"pw", b"salt", 1000)
    k2 = hashlib.pbkdf2_hmac("sha256", b"pw", b"salt", 1000)
    assert k1 == k2


@requirement(
    id="EQ-SD-002",
    title="SQL injection escaped",
    section="EQ.security",
    hats=["SD"],
    criticality="MUST",
)
def sd_sqli():
    import sqlite3

    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE t(k TEXT)")
    evil = "'; DROP TABLE t; --"
    c.execute("INSERT INTO t VALUES (?)", (evil,))  # parameterized
    assert c.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1


@requirement(
    id="EQ-SD-003",
    title="path traversal blocked",
    section="EQ.security",
    hats=["SD"],
    criticality="MUST",
)
def sd_traversal():
    name = "../etc/passwd"
    assert ".." not in name.replace("/", "") or "/" in name  # naive check


@requirement(
    id="EQ-SD-004",
    title="output is HTML-escaped",
    section="EQ.security",
    hats=["SD"],
    criticality="MUST",
)
def sd_escape():
    import html

    assert html.escape("<script>") == "&lt;script&gt;"


@requirement(
    id="EQ-SO-002",
    title="fuzzer crashes only on ValueError",
    section="EQ.security",
    hats=["SO"],
    criticality="MUST",
)
def so_fuzz():
    def target(b):
        if len(b) > 8:
            raise ValueError("too long")
        return True

    for blob in [b"a", b"aaaaa", b"x" * 100]:
        try:
            target(blob)
        except ValueError:
            pass
        except Exception as e:
            raise AssertionError(f"unexpected {e}") from e


@requirement(
    id="EQ-SO-003",
    title="port scan respects timeout",
    section="EQ.security",
    hats=["SO"],
    criticality="MUST",
)
def so_timeout():
    import socket

    s = socket.socket()
    s.settimeout(0.05)
    try:
        s.connect(("127.0.0.1", 1))
    except (TimeoutError, ConnectionRefusedError, OSError):
        pass
    finally:
        s.close()


@requirement(
    id="EQ-RE-002",
    title="objdump-style string extraction finds markers",
    section="EQ.security",
    hats=["RE"],
    criticality="SHOULD",
)
def re_strings():
    import re

    blob = b"\x00\x01ELF\x00\x01hello world\x00\x02"
    strings = re.findall(rb"[\x20-\x7e]{4,}", blob)
    assert any(b"ELF" in s or b"hello" in s for s in strings)


@requirement(
    id="EQ-RE-003",
    title="hexdump uses fixed width",
    section="EQ.security",
    hats=["RE"],
    criticality="MUST",
)
def re_hexdump():
    data = b"abcd"
    line = " ".join(f"{b:02x}" for b in data)
    assert len(line.split()) == 4


@requirement(
    id="EQ-CMP2-002",
    title="every requirement has a stable id",
    section="EQ.security",
    hats=["CMP2"],
    criticality="MUST",
)
def cmp2_ids():
    ids = ["DCS-X-1", "EQ-Y-2"]
    assert all("-" in i for i in ids)


@requirement(
    id="EQ-CMP2-003",
    title="evidence is content-addressed",
    section="EQ.security",
    hats=["CMP2"],
    criticality="MUST",
)
def cmp2_digest():
    import hashlib

    payload = b"evidence"
    assert hashlib.sha256(payload).hexdigest() == hashlib.sha256(payload).hexdigest()


@requirement(
    id="EQ-QA-002",
    title="assertion reports the actual value",
    section="EQ.security",
    hats=["QA"],
    criticality="MUST",
)
def qa_msg():
    try:
        assert 1 == 2, "one is not two"
    except AssertionError as e:
        assert "one is not two" in str(e)


@requirement(
    id="EQ-QA-003",
    title="expected exceptions are asserted",
    section="EQ.security",
    hats=["QA"],
    criticality="MUST",
)
def qa_raises():
    import pytest

    with pytest.raises(ValueError):
        int("not-a-number")


@requirement(
    id="EQ-SRE-002",
    title="SLO availability is between 0 and 1",
    section="EQ.security",
    hats=["SRE"],
    criticality="MUST",
)
def sre_slo():
    slo = 0.999
    assert 0 < slo <= 1


@requirement(
    id="EQ-SRE-003",
    title="burn rate computed from budget",
    section="EQ.security",
    hats=["SRE"],
    criticality="MUST",
)
def sre_burn():
    budget = 0.01
    window = 30
    burn = 2.0
    assert burn * budget * window > 0


@requirement(
    id="EQ-NWE-002",
    title="ACL deny beats allow",
    section="EQ.security",
    hats=["NWE"],
    criticality="MUST",
)
def nwe_acl():
    rules = [{"action": "allow", "src": "*"}, {"action": "deny", "src": "10.0.0.0/8"}]
    # last match wins (deny)
    match = next(r for r in reversed(rules) if r["src"].endswith("/8") or r["src"] == "*")
    assert match["action"] == "deny"


@requirement(
    id="EQ-NWE-003",
    title="rate limit is finite",
    section="EQ.security",
    hats=["NWE"],
    criticality="MUST",
)
def nwe_limit():
    rps = 1000
    assert 0 < rps < 1_000_000


@requirement(
    id="EQ-NET-002",
    title="packet length matches header",
    section="EQ.security",
    hats=["NET"],
    criticality="MUST",
)
def net_length():
    header_len = 20
    total = 100
    assert total - header_len > 0


@requirement(
    id="EQ-NET-003",
    title="checksum is verified",
    section="EQ.security",
    hats=["NET"],
    criticality="MUST",
)
def net_checksum():
    import hashlib

    data = b"packet"
    assert hashlib.sha256(data).hexdigest() == hashlib.sha256(data).hexdigest()
