class C2Server:
    def __init__(self, db_path: str = "b.db"):
        self.db_path = db_path
        self.clients = {}
        self.queue = []
        self.results = {}
        self.kill_switch_active = False

    def register(self, bot_id: str, metadata: dict = None):
        self.clients[bot_id] = {"metadata": metadata or {}, "last_seen": 0.0}
        return True

    def dispatch(self, bot_id: str, task: dict):
        self.queue.append((bot_id, task))
        return True

    def heartbeat(self, bot_id: str):
        if bot_id in self.clients:
            return {"status": "active"}
        return {"status": "unregistered"}

    def complete(self, bot_id: str, task_id: str, result: dict):
        self.results[task_id] = result
        return True
