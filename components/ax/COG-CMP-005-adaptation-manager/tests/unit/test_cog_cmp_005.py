import pytest
from src.public.service import CogCmp005Service

def test_cog_cmp_005_service():
    svc = CogCmp005Service()
    assert svc.component_id == "COG-CMP-005"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
