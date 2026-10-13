"""CodeQL configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_QUERIES: tuple[str, ...] = (
    "codeql/python-queries:codeql-suites/python-security-and-quality.qls",
)

DEFAULT_PACKS: tuple[str, ...] = (
    "codeql/python-queries",
)


@dataclass(frozen=True)
class Config:
    repo_root: Path
    db_dir: Path
    sarif_dir: Path
    source_root: Path
    language: str
    queries: tuple[str, ...]
    packs: tuple[str, ...]
    threads: int
    ram_mb: int
    codeql_home: Path
    codeql_bin: Path
    version: str
    extra_args: tuple[str, ...] = ()
    env: dict[str, str] = field(default_factory=dict)


CodeQLConfig = Config


def load_config(repo_root: Path | None = None,
                version: str = "v2.19.3") -> Config:
    root = (repo_root or Path.cwd()).resolve()
    home = Path(os.environ.get("CODEQL_HOME", str(Path.home() / ".codeql")))
    return Config(
        repo_root=root,
        db_dir=root / ".codeql" / "db",
        sarif_dir=root / ".codeql" / "results",
        source_root=root,
        language="python",
        queries=DEFAULT_QUERIES,
        packs=DEFAULT_PACKS,
        threads=int(os.environ.get("CODEQL_THREADS", "4")),
        ram_mb=int(os.environ.get("CODEQL_RAM_MB", "4096")),
        codeql_home=home,
        codeql_bin=home / "codeql",
        version=version,
        env={"LANG": "en_US.UTF-8"},
    )
