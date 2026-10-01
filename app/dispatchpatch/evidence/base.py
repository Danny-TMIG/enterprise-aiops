class DispatchEvidence:
    def __init__(self, payload: dict):
        self.payload = payload

    def validate(self) -> bool:
        return isinstance(self.payload, dict)
