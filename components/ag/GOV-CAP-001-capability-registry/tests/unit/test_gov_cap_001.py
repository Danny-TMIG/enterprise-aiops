import pytest
from src.public.service import GovCap001Service

def test_gov_cap_001_service():
    svc = GovCap001Service()
    assert svc.component_id == "GOV-CAP-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
