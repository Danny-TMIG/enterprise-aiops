import pytest
from src.public.service import GovInf005Service

def test_gov_inf_005_service():
    svc = GovInf005Service()
    assert svc.component_id == "GOV-INF-005"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
