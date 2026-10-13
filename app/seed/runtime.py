from app.seed.workflow import Workflow, from_cli


class SeedRuntime:
    def __init__(self, root: str = "."):
        from app.core.manifest import Manifest
        self.manifest = Manifest()
        self.root = root

    def start_cli(self, text: str, target: str = None, author: str = None) -> Workflow:
        return self.start(from_cli(text, target=target, author=author))

    def start(self, intent: str) -> Workflow:
        return Workflow(intent=intent, manifest=self.manifest)


def get_seed(*args, **kwargs):
    """Mock get_seed helper for runtime imports."""
    return
