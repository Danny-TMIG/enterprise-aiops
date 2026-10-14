from src.public.service import CmpDat001Service


def test_cmp_dat_001_service():
    svc = CmpDat001Service()
    assert svc.component_id == "CMP-DAT-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
