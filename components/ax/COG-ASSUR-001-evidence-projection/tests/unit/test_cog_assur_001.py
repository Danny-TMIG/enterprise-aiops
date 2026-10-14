import pytest
from src.public.service import CogAssur001Service

def test_cog_assur_001_service():
    svc = CogAssur001Service()
    assert svc.component_id == "COG-ASSUR-001"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
