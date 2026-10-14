from app.dispatchpatch.orchestration.base import BaseOrchestrator


class ServiceNowOrchestrator(BaseOrchestrator):
    def orchestrate(self, task: str) -> str:
        return f"ServiceNow Orchestrated: {task}"
