from src.public.service import CmpExe005Service


def test_cmp_exe_005_service():
    svc = CmpExe005Service()
    assert svc.component_id == "CMP-EXE-005"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
