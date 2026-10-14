import pytest
from src.public.service import CmpExe001Service

def test_cmp_exe_001_service():
    svc = CmpExe001Service()
    assert svc.component_id == "CMP-EXE-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
