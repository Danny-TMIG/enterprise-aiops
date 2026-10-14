import importlib.util, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "sched",
    ROOT / "components/ac/CMP-EXE-004-scheduler/src/public/mod004.py",
)
m = importlib.util.module_from_spec(spec); sys.modules["sched"] = m
spec.loader.exec_module(m)


def test_schedule_fits_three_jobs():
    s = m.Scheduler(cpu_cores=4, memory_gb=8)
    s.submit("a", cpu_cores=1, memory_gb=1)
    s.submit("b", cpu_cores=2, memory_gb=2)
    placed = s.schedule()
    assert set(placed) == {"a", "b"}


def test_no_preemption_without_emergency():
    s = m.Scheduler(cpu_cores=1, memory_gb=1)
    s.submit("hog", cpu_cores=1, memory_gb=1, protect_from_preemption=True)
    s.schedule()
    s.submit("late", cpu_cores=1, memory_gb=1)  # not emergency
    placed = s.schedule()
    assert placed == []
    assert s.stats()["running"] == ["hog"]


def test_emergency_preempts_unprotected():
    s = m.Scheduler(cpu_cores=1, memory_gb=1)
    s.submit("hog", cpu_cores=1, memory_gb=1, protect_from_preemption=False)
    s.schedule()
    s.submit("911", cpu_cores=1, memory_gb=1, emergency_reserve=True)
    placed = s.schedule()
    assert placed == ["911"]
    assert "hog" not in s.stats()["running"]
