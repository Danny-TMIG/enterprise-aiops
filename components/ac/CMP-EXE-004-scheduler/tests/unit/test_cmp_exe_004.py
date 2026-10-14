import pytest
from src.public.service import CmpExe004Service

def test_cmp_exe_004_service():
    svc = CmpExe004Service()
    assert svc.component_id == "CMP-EXE-004"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
