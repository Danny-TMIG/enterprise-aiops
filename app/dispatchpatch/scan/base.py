class BaseScan:
    def scan(self, code: str) -> dict:
        return {"status": "clean", "code": code}
