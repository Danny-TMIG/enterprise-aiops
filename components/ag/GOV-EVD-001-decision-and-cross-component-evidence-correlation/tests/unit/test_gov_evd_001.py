import pytest
from src.public.service import GovEvd001Service

def test_gov_evd_001_service():
    svc = GovEvd001Service()
    assert svc.component_id == "GOV-EVD-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
