"""The moat must not lie downward.

If the reality probe says 1.0, the moat's X axis must reflect that
on the subsystems that *define* reality.
"""
import json
from pathlib import Path

from app.moat.axes import score_all, score_subsystem
from app.moat.moat import MoatMesh, record_run
from app.moat.runtime import MoatRuntime
from app.reality.probe import probe_reality

ROOT = Path(__file__).resolve().parent.parent


def test_reality_definition_files_score_x_1():
    """Files that define reality must score X = 1.0."""
    for rel in ("app/reality/probe.py",
                "app/reality/install.py",
                "app/proprietary/base.py",
                "app/proprietary/registry.py",
                "app/frontier/dis.py",
                "app/dis/models/local_mlx.py"):
        p = ROOT / rel
        assert p.exists(), rel
        sc = score_subsystem(rel, p, p.read_text())
        assert sc.x == 1.0, f"{rel} X={sc.x}"


def test_local_impl_scores_x_ge_09():
    """Files with a local implementation score X >= 0.9."""
    p = ROOT / "app/proprietary/microsoft.py"
    sc = score_subsystem("microsoft", p, p.read_text())
    assert sc.x >= 0.9, sc.x


def test_reality_probe_and_moat_agree():
    """Probe reality fraction >= 0.9 ⇒ moat X >= 0.5 on the app/."""
    probe = probe_reality().score()
    if probe["reality_fraction"] < 0.9:
        return  # skip: reality probe says we are not there yet
    scores = score_all(ROOT, scope="app")
    avg_x = sum(s.x for s in scores) / max(1, len(scores))
    assert avg_x >= 0.5, f"moat X={avg_x} too low for real={probe}"


def test_moat_3axis_is_positive_when_reality_is():
    rt = MoatRuntime(root=str(ROOT))
    s = rt.score(scope="app")
    # if reality > 0.9 and E ~ 1, moat must be above 0
    if s["axes"]["real"] > 0.5 and s["axes"]["exists"] > 0.9:
        assert s["moat_3axis"] > 0, s


def test_execution_history_is_recorded():
    record_run({"id": "test-run", "kernel": {"status": "PASS"},
                "cpvo": {"cpvo_usd": 0.0}}, merged=False)
    mesh = MoatMesh().refresh()
    f = mesh.equation.factors()
    assert f["X_h"] > 0.0, f
    assert f["P_g"] > 0.0, f


def test_composite_product_positive():
    mesh = MoatMesh().refresh()
    d = mesh.to_dict()
    # with the SBOM on disk, E_g >= 0.5; with runs recorded, X_h > 0
    assert d["factors"]["C_g"] > 0
    assert d["factors"]["S_g"] > 0
    assert d["factors"]["E_g"] > 0
    assert d["factors"]["Q_g"] > 0
    assert d["factors"]["K_g"] > 0


def test_status_serializable():
    rt = MoatRuntime(root=str(ROOT))
    json.dumps(rt.status(), default=str)
