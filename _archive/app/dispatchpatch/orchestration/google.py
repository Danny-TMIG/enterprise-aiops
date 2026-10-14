from app.dispatchpatch.orchestration.base import BaseOrchestrator


class GoogleOrchestrator(BaseOrchestrator):
    def orchestrate(self, task: str) -> str:
        return f"Google Cloud Orchestrated: {task}"
