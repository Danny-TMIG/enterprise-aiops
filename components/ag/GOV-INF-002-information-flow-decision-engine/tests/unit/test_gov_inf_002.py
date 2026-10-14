import pytest
from src.public.service import GovInf002Service

def test_gov_inf_002_service():
    svc = GovInf002Service()
    assert svc.component_id == "GOV-INF-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
