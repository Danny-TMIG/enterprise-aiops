import pytest
from src.public.service import CmpExe007Service

def test_cmp_exe_007_service():
    svc = CmpExe007Service()
    assert svc.component_id == "CMP-EXE-007"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
