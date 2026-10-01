from typing import Dict, Type
from app.dispatchpatch.scan.base import BaseScan

class ScanRegistry:
    _scans: Dict[str, Type[BaseScan]] = {}

    @classmethod
    def register(cls, name: str, scan_cls: Type[BaseScan]):
        cls._scans[name] = scan_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseScan]:
        return cls._scans.get(name, BaseScan)
