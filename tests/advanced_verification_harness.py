from hypothesis.stateful import RuleBasedStateMachine, bundle, rule


class EnterpriseStateVerifier(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.locked = False
        self.owner = None
        self.corpus_registry = set()
        self.audit_trail = []

    @rule(client_id=bundle("clients"))
    def acquire_lock(self, client_id: str):
        if not self.locked:
            self.locked = True
            self.owner = client_id
            self.audit_trail.append(f"LOCK:{client_id}")

    @rule(client_id=bundle("clients"))
    def release_lock(self, client_id: str):
        if self.locked and self.owner == client_id:
            self.locked = False
            self.owner = None
            self.audit_trail.append(f"UNLOCK:{client_id}")

    @rule(corpus_hash=bundle("hashes"))
    def commit_corpus(self, corpus_hash: str):
        if self.locked:
            self.corpus_registry.add(corpus_hash)
            self.audit_trail.append(f"COMMIT:{corpus_hash}")

    def invariant(self):
        if self.locked:
            assert self.owner is not None, "Invariant Violation: Locked state missing owner."
        assert len(self.audit_trail) < 1000, "State space overflow protection triggered."

TestEnterpriseStateMachine = EnterpriseStateVerifier.TestCase
