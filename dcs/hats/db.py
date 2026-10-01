"""DB — database. SQLite in-memory CRUD."""

import sqlite3

from dcs.generate import requirement


def fresh() -> sqlite3.Connection:
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE runs(id INTEGER PRIMARY KEY, digest TEXT NOT NULL)")
    return c


@requirement(
    id="DCS-DB-001",
    title="insert + select round-trips",
    section="DB.database",
    hats=["DB"],
    criticality="MUST",
)
def test():
    c = fresh()
    c.execute("INSERT INTO runs(digest) VALUES (?)", ("sha256:abc",))
    c.commit()
    row = c.execute("SELECT digest FROM runs").fetchone()
    assert row == ("sha256:abc",)
