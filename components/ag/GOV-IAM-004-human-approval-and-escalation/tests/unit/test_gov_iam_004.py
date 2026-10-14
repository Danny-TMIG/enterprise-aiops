from src.public.service import GovIam004Service


def test_gov_iam_004_service():
    svc = GovIam004Service()
    assert svc.component_id == "GOV-IAM-004"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
