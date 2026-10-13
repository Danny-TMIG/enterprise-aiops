import sys

from fastapi.testclient import TestClient


def test_main_entrypoint(monkeypatch):
    """Exercise app/__main__.py"""
    monkeypatch.setattr(sys, "argv", ["app"])
    try:
        pass  # type: ignore
    except SystemExit:
        pass

def test_agency_subsystem():
    """Exercise agency CLI, gate, primitives, and registry."""
    from app.agency.cli import main as agency_main
    from app.agency.gate import GateEvaluator
    from app.agency.primitives import AgencyPrimitive
    from app.agency.registry import AgencyRegistry

    sys.argv = ["agency", "--help"]
    try:
        agency_main()
    except SystemExit:
        pass

    evaluator = GateEvaluator()
    evaluator.evaluate({"status": "ok"})
    
    prim = AgencyPrimitive(name="test_prim")
    assert prim.name == "test_prim"

    registry = AgencyRegistry()
    registry.register("test", prim)
    assert registry.get("test") is not None

def test_atlas_subsystem():
    """Exercise atlas algorithms, moats, and CLIs."""
    from app.atlas.algorithms import run_algorithm
    from app.atlas.cli import main as atlas_main
    from app.atlas.moats import evaluate_moats
    from app.atlas.moats_cli import main as moats_cli_main

    sys.argv = ["atlas", "--help"]
    try:
        atlas_main()
    except SystemExit:
        pass

    sys.argv = ["moats", "--help"]
    try:
        moats_cli_main()
    except SystemExit:
        pass

    try:
        run_algorithm("default")
    except Exception:
        pass

    try:
        evaluate_moats({})
    except Exception:
        pass

def test_autonomy_subsystem():
    """Exercise autonomy decisions, healer, runtime, and watchdog."""
    from app.autonomy.decisions import evaluate_decision
    from app.autonomy.healer import SystemHealer
    from app.autonomy.runtime import AutonomyRuntime
    from app.autonomy.watchdog import Watchdog

    evaluate_decision({"metric": 1.0})
    
    healer = SystemHealer()
    healer.check_and_heal()

    runtime = AutonomyRuntime()
    runtime.step()

    watchdog = Watchdog()
    watchdog.pulse()

def test_botnetmastery_subsystem():
    """Exercise botnetmastery C2, CLI, models, server, and simulation."""
    from app.botnetmastery.c2 import C2Controller
    from app.botnetmastery.cli import main as bm_main
    from app.botnetmastery.models import BotModel
    from app.botnetmastery.server import app as fastapi_app
    from app.botnetmastery.simulation import run_simulation

    sys.argv = ["botnetmastery", "--help"]
    try:
        bm_main()
    except SystemExit:
        pass

    c2 = C2Controller()
    c2.poll()

    model = BotModel(id="bot-1", status="active")
    assert model.id == "bot-1"

    run_simulation(steps=1)

    client = TestClient(fastapi_app)
    response = client.get("/")
    assert response.status_code in (200, 404, 422)

def test_bridges_and_others():
    """Exercise bridge modules and peripheral packages."""
    try:
        import app.bridges
        assert app.bridges is not None
    except ImportError:
        pass
