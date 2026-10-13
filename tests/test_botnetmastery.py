import pytest

from app.botnetmastery.c2 import C2Server
from app.botnetmastery.models import Bot, Task
from app.botnetmastery.simulation import Simulation


@pytest.fixture
def srv(tmp_path):
    s = C2Server(str(tmp_path / "b.db"))
    yield s
    s.close()


def test_register_bot(srv):
    b = Bot.new("h1", "linux", "x86_64")
    srv.register_bot(b)
    assert srv.get_bot(b.id)["hostname"] == "h1"


def test_queue_and_dispatch(srv):
    b = Bot.new("h1", "linux", "x86_64")
    srv.register_bot(b)
    tid = srv.queue_task(Task.new(b.id, "ping", {"n": 1}))
    row = srv.dispatch(b.id)
    assert row["id"] == tid
    assert row["status"] == "sent"


def test_complete_writes_result(srv):
    b = Bot.new("h1", "linux", "x86_64")
    srv.register_bot(b)
    tid = srv.queue_task(Task.new(b.id, "ping", {}))
    srv.dispatch(b.id)
    srv.complete(tid, b.id, '{"ok":true}', success=True)
    res = srv.results_for(b.id)
    assert len(res) == 1
    assert res[0]["success"] == 1


def test_kill_switch_blocks_queue(srv):
    b = Bot.new("h1", "linux", "x86_64")
    srv.register_bot(b)
    srv.engage_kill_switch("test")
    with pytest.raises(RuntimeError):
        srv.queue_task(Task.new(b.id, "ping", {}))
    assert srv.kill_switch_engaged()


def test_kill_switch_blocks_dispatch(srv):
    b = Bot.new("h1", "linux", "x86_64")
    srv.register_bot(b)
    srv.queue_task(Task.new(b.id, "ping", {}))
    srv.engage_kill_switch("test")
    assert srv.dispatch(b.id) is None


def test_revoke_all_commands(srv):
    b = Bot.new("h1", "linux", "x86_64")
    srv.register_bot(b)
    srv.queue_task(Task.new(b.id, "ping", {}))
    srv.queue_task(Task.new(b.id, "inventory", {}))
    n = srv.revoke_all_commands()
    assert n >= 2


def test_simulation_tick(srv):
    sim = Simulation(srv, seed=1)
    sim.spawn(5)
    sim.queue_broadcast("heartbeat", {"interval": 30})
    stats = sim.tick()
    assert stats["heartbeats"] == 5
    assert stats["dispatched"] == 5
    assert stats["completed"] == 5


def test_simulation_kill_switch_halts(srv):
    sim = Simulation(srv, seed=1)
    sim.spawn(3)
    sim.queue_broadcast("heartbeat", {})
    srv.engage_kill_switch("halt")
    stats = sim.tick()
    assert stats["dispatched"] == 0
    assert stats["skipped"] >= 3


def test_heartbeat_updates_last_seen(srv):
    b = Bot.new("h1", "linux", "x86_64")
    srv.register_bot(b)
    before = srv.get_bot(b.id)["last_seen"]
    srv.heartbeat(b.id)
    after = srv.get_bot(b.id)["last_seen"]
    assert after >= before


def test_pending_tasks_shape(srv):
    b = Bot.new("h1", "linux", "x86_64")
    srv.register_bot(b)
    srv.queue_task(Task.new(b.id, "ping", {}))
    pending = srv.pending_tasks()
    assert len(pending) == 1
    assert pending[0]["status"] == "queued"
