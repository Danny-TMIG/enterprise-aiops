import pytest
from src.public.service import GovEvd003Service

def test_gov_evd_003_service():
    svc = GovEvd003Service()
    assert svc.component_id == "GOV-EVD-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
