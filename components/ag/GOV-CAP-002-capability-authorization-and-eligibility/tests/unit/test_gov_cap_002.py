import pytest
from src.public.service import GovCap002Service

def test_gov_cap_002_service():
    svc = GovCap002Service()
    assert svc.component_id == "GOV-CAP-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
