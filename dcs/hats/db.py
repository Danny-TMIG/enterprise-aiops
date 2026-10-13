"""DB — database. SQLite in-memory CRUD."""

import sqlite3  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def fresh() -> sqlite3.Connection:  # pragma: no cover
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE runs(id INTEGER PRIMARY KEY, digest TEXT NOT NULL)")
    return c  # pragma: no cover


@requirement(
    id="DCS-DB-001",
    title="insert + select round-trips",
    section="DB.database",
    hats=["DB"],
    criticality="MUST",
)
def test():  # pragma: no cover
    c = fresh()
    c.execute("INSERT INTO runs(digest) VALUES (?)", ("sha256:abc",))
    c.commit()
    row = c.execute("SELECT digest FROM runs").fetchone()
    assert row == ("sha256:abc",)
