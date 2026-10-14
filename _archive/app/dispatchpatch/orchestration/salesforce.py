from app.dispatchpatch.orchestration.base import BaseOrchestrator


class SalesforceOrchestrator(BaseOrchestrator):
    def orchestrate(self, task: str) -> str:
        return f"Salesforce Orchestrated: {task}"
