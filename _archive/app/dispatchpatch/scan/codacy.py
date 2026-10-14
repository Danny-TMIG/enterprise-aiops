from app.dispatchpatch.scan.base import BaseScan


class CodacyScan(BaseScan):
    def scan(self, code: str) -> dict:
        res = super().scan(code)
        res["scanner"] = "codacy"
        return res
