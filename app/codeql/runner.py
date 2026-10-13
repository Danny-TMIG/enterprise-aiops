"""Real CodeQL CLI runner. No stubs.

install_cli   — download and unpack the CodeQL bundle.
cli_present   — check the binary is executable.
cli_version   — run `codeql version` and parse the output.
create_database — `codeql database create` for Python.
analyze       — `codeql database analyze` producing SARIF.
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from app.codeql.config import Config, load_config


@dataclass
class Database:
    path: Path
    language: str
    created: bool
    size_bytes: int = 0
    log: str = ""

    def to_dict(self) -> dict:
        return {"path": str(self.path), "language": self.language,
                "created": self.created, "size_bytes": self.size_bytes}


@dataclass
class Analysis:
    sarif_path: Path
    queries: tuple[str, ...]
    exit_code: int
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and self.sarif_path.exists()


# ── CLI lifecycle ───────────────────────────────────────────────
def cli_present(cfg: Config | None = None) -> bool:
    cfg = cfg or load_config()
    return cfg.codeql_bin.is_file() and os.access(cfg.codeql_bin, os.X_OK)


def cli_version(cfg: Config | None = None) -> str:
    cfg = cfg or load_config()
    if not cli_present(cfg):
        return "not-installed"
    try:
        r = subprocess.run([str(cfg.codeql_bin), "version"],
                           capture_output=True, text=True, timeout=30)
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.lower().startswith("version"):
                return line.split(":", 1)[1].strip() if ":" in line else line
        return r.stdout.strip().splitlines()[0] if r.stdout.strip() else "unknown"
    except Exception as e:
        return f"error: {e}"


def _bundle_url(version: str) -> str:
    machine = platform.machine().lower()
    if machine in ("arm64", "aarch64"):
        bundle = "codeql-bundle-osx-arm64.tar.gz"
    elif "darwin" in platform.system().lower():
        bundle = "codeql-bundle-osx64.tar.gz"
    elif platform.system().lower() == "linux":
        bundle = "codeql-bundle-linux64.tar.gz"
    else:
        bundle = "codeql-bundle-osx64.tar.gz"
    return (f"https://github.com/github/codeql-action/releases/download/"
            f"codeql-bundle-{version}/{bundle}")


def install_cli(cfg: Config | None = None,
                force: bool = False) -> Config:
    cfg = cfg or load_config()
    if cli_present(cfg) and not force:
        return cfg
    cfg.codeql_home.mkdir(parents=True, exist_ok=True)
    url = _bundle_url(cfg.version)
    tmp = Path("/tmp") / f"codeql-{cfg.version}.tar.gz"
    print(f"  downloading {url}")
    urllib.request.urlretrieve(url, tmp)
    print(f"  unpacking {tmp} -> {cfg.codeql_home}")
    with tarfile.open(tmp, "r:gz") as tf:
        members = tf.getmembers()
        strip = 1
        prefix = None
        for m in members:
            parts = Path(m.name).parts
            if parts and prefix is None:
                prefix = parts[0]
            if prefix and parts and parts[0] == prefix:
                m.name = str(Path(*parts[strip:]))
            else:
                m.name = ""
        tf.extractall(cfg.codeql_home)
    tmp.unlink(missing_ok=True)
    # make binary executable
    for candidate in (cfg.codeql_home / "codeql",
                      cfg.codeql_home / "codeql" / "codeql"):
        if candidate.is_file():
            candidate.chmod(0o755)
    if not cli_present(cfg):
        raise RuntimeError(
            f"codeql binary not found after install at {cfg.codeql_bin}")
    return cfg


# ── database ────────────────────────────────────────────────────
def create_database(cfg: Config | None = None,
                    force: bool = False,
                    overrides: dict[str, str] | None = None) -> Database:
    cfg = cfg or load_config()
    if not cli_present(cfg):
        raise RuntimeError("CodeQL CLI not present; run install_cli()")
    db = cfg.db_dir
    if db.exists() and not force:
        size = _dir_size(db)
        return Database(path=db, language=cfg.language, created=True,
                        size_bytes=size, log="reused")
    if db.exists():
        shutil.rmtree(db)
    db.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(cfg.codeql_bin), "database", "create", str(db),
        f"--language={cfg.language}",
        f"--source-root={cfg.source_root}",
        f"--threads={cfg.threads}",
        "--overwrite",
    ]
    env = {**os.environ, **cfg.env}
    if overrides:
        env.update(overrides)
    print(f"  running: {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError("database create failed: " + r.stderr[-2000:])
    return Database(path=db, language=cfg.language, created=True,
                    size_bytes=_dir_size(db), log=r.stdout[-2000:])


# ── analysis ────────────────────────────────────────────────────
def analyze(cfg: Config | None = None,
            db: Database | None = None,
            download: bool = True,
            extra_queries: list[str] | None = None) -> Analysis:
    cfg = cfg or load_config()
    if not cli_present(cfg):
        raise RuntimeError("CodeQL CLI not present; run install_cli()")
    if db is None:
        db = create_database(cfg)
    cfg.sarif_dir.mkdir(parents=True, exist_ok=True)
    sarif = cfg.sarif_dir / "results.sarif"
    queries = list(cfg.queries) + list(extra_queries or [])
    cmd = [
        str(cfg.codeql_bin), "database", "analyze", str(db.path),
        "--format=sarif-latest",
        f"--output={sarif}",
        f"--threads={cfg.threads}",
    ]
    if download:
        cmd.append("--download")
    cmd.extend(queries)
    cmd.extend(cfg.extra_args)
    env = {**os.environ, **cfg.env}
    print(f"  running: {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return Analysis(sarif_path=sarif, queries=tuple(queries),
                    exit_code=r.returncode, stdout=r.stdout[-4000:],
                    stderr=r.stderr[-4000:])


# ── helpers ─────────────────────────────────────────────────────
def _dir_size(path: Path) -> int:
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_size
            except OSError:
                pass
    return total
