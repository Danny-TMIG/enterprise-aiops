from app.dispatchpatch.orchestration.base import BaseOrchestrator


class MicrosoftOrchestrator(BaseOrchestrator):
    def orchestrate(self, task: str) -> str:
        return f"Azure Orchestrated: {task}"
