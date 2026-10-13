"""Configuration management for CodeQL analysis."""

import os
from pathlib import Path
from typing import Any


class CodeQLConfig:
    def __init__(self, workspace_dir: str | None = None):
        self.workspace_dir = Path(workspace_dir or os.getcwd())
        self.codeql_dir = self.workspace_dir / ".codeql"
        self.db_path = self.codeql_dir / "db"
        self.results_dir = self.codeql_dir / "results"
        self.results_sarif = self.results_dir / "results.sarif"
        self.binary_path = Path(os.environ.get("CODEQL_PATH", "/Users/metadusa/.codeql/codeql"))
        
    def ensure_directories(self) -> None:
        self.codeql_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "workspace_dir": str(self.workspace_dir),
            "codeql_dir": str(self.codeql_dir),
            "db_path": str(self.db_path),
            "results_sarif": str(self.results_sarif),
            "binary_path": str(self.binary_path),
        }
