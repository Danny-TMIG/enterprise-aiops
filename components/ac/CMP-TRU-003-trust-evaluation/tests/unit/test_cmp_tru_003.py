from src.public.service import CmpTru003Service


def test_cmp_tru_003_service():
    svc = CmpTru003Service()
    assert svc.component_id == "CMP-TRU-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
