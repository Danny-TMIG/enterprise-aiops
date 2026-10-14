from src.public.service import CmpExe006Service


def test_cmp_exe_006_service():
    svc = CmpExe006Service()
    assert svc.component_id == "CMP-EXE-006"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
