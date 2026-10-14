import pytest
from src.public.service import CogRea003Service

def test_cog_rea_003_service():
    svc = CogRea003Service()
    assert svc.component_id == "COG-REA-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
