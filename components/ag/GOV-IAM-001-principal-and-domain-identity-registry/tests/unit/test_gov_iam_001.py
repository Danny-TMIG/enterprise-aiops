import pytest
from src.public.service import GovIam001Service

def test_gov_iam_001_service():
    svc = GovIam001Service()
    assert svc.component_id == "GOV-IAM-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
