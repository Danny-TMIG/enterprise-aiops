import pytest
from src.public.service import GovKrn002Service

def test_gov_krn_002_service():
    svc = GovKrn002Service()
    assert svc.component_id == "GOV-KRN-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
