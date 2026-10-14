import importlib.util, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "quota",
    ROOT / "components/ac/CMP-RES-007-admission-quota-and-lease-manager/src/public/mod007.py",
)
m = importlib.util.module_from_spec(spec); sys.modules["quota"] = m
spec.loader.exec_module(m)


def test_hierarchical_admission():
    root = m.QuotaNode("root", 8, 16)
    ops = root.add_child("ops", 4, 8)
    ops.add_child("ops-a", 2, 4)
    ac = m.AdmissionController(root)
    lease = ac.request("l1", "root/ops/ops-a", cpu_cores=2, memory_gb=4)
    assert lease.lease_id == "l1"
    assert root.cpu_used == 2 and ops.cpu_used == 2


def test_quota_exceeded_rejected():
    root = m.QuotaNode("root", 2, 4)
    ac = m.AdmissionController(root)
    ac.request("l1", "root", cpu_cores=2, memory_gb=4)
    try:
        ac.request("l2", "root", cpu_cores=1, memory_gb=1)
    except m.QuotaError:
        return
    raise AssertionError("expected QuotaError")


def test_reap_expired_returns_resources():
    root = m.QuotaNode("root", 4, 8)
    ac = m.AdmissionController(root)
    ac.request("l1", "root", cpu_cores=4, memory_gb=8, ttl_seconds=0)
    expired = ac.reap_expired()
    assert expired == ["l1"]
    assert root.cpu_used == 0 and root.mem_used == 0
