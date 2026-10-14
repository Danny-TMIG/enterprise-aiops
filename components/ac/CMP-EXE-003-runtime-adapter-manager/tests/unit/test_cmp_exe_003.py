import pytest
from src.public.service import CmpExe003Service

def test_cmp_exe_003_service():
    svc = CmpExe003Service()
    assert svc.component_id == "CMP-EXE-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
