
from app.dispatchpatch.scan.base import BaseScan


class ScanRegistry:
    _scans: dict[str, type[BaseScan]] = {}

    @classmethod
    def register(cls, name: str, scan_cls: type[BaseScan]):
        cls._scans[name] = scan_cls

    @classmethod
    def get(cls, name: str) -> type[BaseScan]:
        return cls._scans.get(name, BaseScan)
