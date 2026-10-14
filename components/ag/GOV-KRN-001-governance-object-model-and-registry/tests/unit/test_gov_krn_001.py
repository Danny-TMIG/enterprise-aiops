import pytest
from src.public.service import GovKrn001Service

def test_gov_krn_001_service():
    svc = GovKrn001Service()
    assert svc.component_id == "GOV-KRN-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
