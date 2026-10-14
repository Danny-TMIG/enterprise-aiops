import pytest
from src.public.service import GovIam002Service

def test_gov_iam_002_service():
    svc = GovIam002Service()
    assert svc.component_id == "GOV-IAM-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
