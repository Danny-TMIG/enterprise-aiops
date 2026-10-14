"""DBA — query planner uses the index."""

import sqlite3  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def setup() -> sqlite3.Connection:  # pragma: no cover
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE runs(id INTEGER PRIMARY KEY, digest TEXT)")
    c.execute("CREATE INDEX ix_digest ON runs(digest)")
    for i in range(50):
        c.execute("INSERT INTO runs(digest) VALUES (?)", (f"sha256:{i:040x}",))
    c.commit()
    return c  # pragma: no cover


def plan_uses_index(c, sql) -> bool:  # pragma: no cover
    rows = c.execute("EXPLAIN QUERY PLAN " + sql).fetchall()
    return any("INDEX" in str(r) for r in rows)  # pragma: no cover


@requirement(
    id="DCS-DBA-001",
    title="lookup on digest uses the index",
    section="DBA.dba",
    hats=["DBA"],
    criticality="MUST",
)
def test():  # pragma: no cover
    c = setup()
    sql = "SELECT id FROM runs WHERE digest = 'sha256:0'"
    assert plan_uses_index(c, sql)
