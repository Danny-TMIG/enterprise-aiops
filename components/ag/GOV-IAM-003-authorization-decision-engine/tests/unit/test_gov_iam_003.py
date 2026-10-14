import pytest
from src.public.service import GovIam003Service

def test_gov_iam_003_service():
    svc = GovIam003Service()
    assert svc.component_id == "GOV-IAM-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
