from app.dispatchpatch.scan.base import BaseScan


class CodeQLScan(BaseScan):
    def scan(self, code: str) -> dict:
        res = super().scan(code)
        res["scanner"] = "codeql"
        return res
