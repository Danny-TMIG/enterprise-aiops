from src.public.service import GovAdm002Service


def test_gov_adm_002_service():
    svc = GovAdm002Service()
    assert svc.component_id == "GOV-ADM-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
