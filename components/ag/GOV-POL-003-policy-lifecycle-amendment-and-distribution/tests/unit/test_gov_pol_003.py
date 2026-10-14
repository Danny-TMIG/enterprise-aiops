import pytest
from src.public.service import GovPol003Service

def test_gov_pol_003_service():
    svc = GovPol003Service()
    assert svc.component_id == "GOV-POL-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
