import pytest
from src.public.service import CogCmp004Service

def test_cog_cmp_004_service():
    svc = CogCmp004Service()
    assert svc.component_id == "COG-CMP-004"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
