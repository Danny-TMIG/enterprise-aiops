import pytest
from src.public.service import GovInf004Service

def test_gov_inf_004_service():
    svc = GovInf004Service()
    assert svc.component_id == "GOV-INF-004"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
