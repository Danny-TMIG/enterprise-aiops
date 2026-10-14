import pytest
from src.public.service import CogRea005Service

def test_cog_rea_005_service():
    svc = CogRea005Service()
    assert svc.component_id == "COG-REA-005"
    res = svc.execute_operation({"test": True})
    assert res["status"] == "success"
