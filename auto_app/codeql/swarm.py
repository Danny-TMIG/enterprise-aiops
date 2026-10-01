"""Swarm orchestration runner for CodeQL multi-threaded scans."""

from typing import Dict, Any
from .runner import CodeQLRunner
from .policy import CodeQLPolicy
from .report import CodeQLReporter

class CodeQLSwarm:
    def __init__(self, runner: CodeQLRunner = None, policy: CodeQLPolicy = None):
        self.runner = runner or CodeQLRunner()
        self.policy = policy or CodeQLPolicy()
        self.reporter = CodeQLReporter(self.runner.config.results_sarif)

    def execute_pipeline(self) -> Dict[str, Any]:
        created = self.runner.create_database()
        analyzed = self.runner.analyze_database()
        policy_res = self.policy.evaluate(self.runner.config.results_sarif)
        summary = self.reporter.generate_summary()

        return {
            "database_created": created,
            "database_analyzed": analyzed,
            "policy": policy_res,
            "summary": summary
        }
