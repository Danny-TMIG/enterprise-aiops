import pytest
from src.public.service import CogAssur003Service

def test_cog_assur_003_service():
    svc = CogAssur003Service()
    assert svc.component_id == "COG-ASSUR-003"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
