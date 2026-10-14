from src.public.service import CmpExe002Service


def test_cmp_exe_002_service():
    svc = CmpExe002Service()
    assert svc.component_id == "CMP-EXE-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
