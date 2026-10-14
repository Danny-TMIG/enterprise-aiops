import pytest
from src.public.service import CogRea004Service

def test_cog_rea_004_service():
    svc = CogRea004Service()
    assert svc.component_id == "COG-REA-004"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
