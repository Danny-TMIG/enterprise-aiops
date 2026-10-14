from src.public.service import CmpTru002Service


def test_cmp_tru_002_service():
    svc = CmpTru002Service()
    assert svc.component_id == "CMP-TRU-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
