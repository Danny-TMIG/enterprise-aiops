from src.public.service import GovAdm001Service


def test_gov_adm_001_service():
    svc = GovAdm001Service()
    assert svc.component_id == "GOV-ADM-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
