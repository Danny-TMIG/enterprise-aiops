import pytest
from src.public.service import GovInf001Service

def test_gov_inf_001_service():
    svc = GovInf001Service()
    assert svc.component_id == "GOV-INF-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
