import pytest
from src.public.service import CogRea001Service

def test_cog_rea_001_service():
    svc = CogRea001Service()
    assert svc.component_id == "COG-REA-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
