import pytest
from src.public.service import CogRea002Service

def test_cog_rea_002_service():
    svc = CogRea002Service()
    assert svc.component_id == "COG-REA-002"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
