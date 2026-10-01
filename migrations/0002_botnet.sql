-- Defensive botnet C2 simulation schema.
-- Applied to SQLite for local tests; portable to Postgres.

CREATE TABLE IF NOT EXISTS bots (
    id           TEXT PRIMARY KEY,
    hostname     TEXT NOT NULL,
    os           TEXT NOT NULL,
    arch         TEXT NOT NULL,
    first_seen   TEXT NOT NULL DEFAULT (datetime('now')),
    last_seen    TEXT NOT NULL DEFAULT (datetime('now')),
    status       TEXT NOT NULL DEFAULT 'idle',   -- idle|busy|dead
    tags         TEXT NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    bot_id       TEXT NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
    kind         TEXT NOT NULL,
    payload      TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    dispatched_at TEXT,
    completed_at TEXT,
    status       TEXT NOT NULL DEFAULT 'queued'  -- queued|sent|done|failed
);

CREATE TABLE IF NOT EXISTS commands (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id      INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    issued_by    TEXT NOT NULL,
    issued_at    TEXT NOT NULL DEFAULT (datetime('now')),
    signature    TEXT NOT NULL,
    revoked      INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS results (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id      INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    bot_id       TEXT NOT NULL REFERENCES bots(id) ON DELETE CASCADE,
    output       TEXT NOT NULL,
    received_at  TEXT NOT NULL DEFAULT (datetime('now')),
    success      INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS kill_switch (
    id           INTEGER PRIMARY KEY CHECK (id = 1),
    engaged      INTEGER NOT NULL DEFAULT 0,
    engaged_at   TEXT,
    reason       TEXT
);
INSERT OR IGNORE INTO kill_switch(id, engaged) VALUES (1, 0);

CREATE INDEX IF NOT EXISTS idx_tasks_bot   ON tasks(bot_id, status);
CREATE INDEX IF NOT EXISTS idx_results_bot ON results(bot_id, received_at DESC);
