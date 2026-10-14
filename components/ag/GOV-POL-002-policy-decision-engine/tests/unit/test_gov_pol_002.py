import pytest
from src.public.service import GovPol002Service

def test_gov_pol_002_service():
    svc = GovPol002Service()
    assert svc.component_id == "GOV-POL-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
