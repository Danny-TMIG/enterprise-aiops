from src.public.service import GovKrn003Service


def test_gov_krn_003_service():
    svc = GovKrn003Service()
    assert svc.component_id == "GOV-KRN-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
