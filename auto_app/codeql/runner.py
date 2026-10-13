"""CodeQL execution runner handling database creation and analysis."""

import logging
import subprocess

from .config import CodeQLConfig

logger = logging.getLogger(__name__)

class CodeQLRunner:
    def __init__(self, config: CodeQLConfig | None = None):
        self.config = config or CodeQLConfig()
        self.config.ensure_directories()

    def run_command(self, args: list[str]) -> subprocess.CompletedProcess:
        cmd = [str(self.config.binary_path)] + args
        logger.info("running: %s", " ".join(cmd))
        print(f" running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("CodeQL command failed: %s", result.stderr)
        return result

    def create_database(self, source_root: str | None = None, language: str = "python") -> bool:
        src = source_root or str(self.config.workspace_dir)
        args = ["create", str(self.config.db_path), f"--language={language}", f"--source-root={src}", "--overwrite"]
        res = self.run_command(args)
        return res.returncode == 0

    def analyze_database(self, query_suite: str = "codeql/python-queries:codeql-suites/python-security-and-quality.qls", threads: int = 4) -> bool:
        args = [
            "analyze",
            str(self.config.db_path),
            "--format=sarif-latest",
            f"--output={self.config.results_sarif}",
            f"--threads={threads}",
            "--download",
            query_suite
        ]
        res = self.run_command(args)
        return res.returncode == 0
