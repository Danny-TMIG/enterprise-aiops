"""Control plane routes to a sovereign node."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_nodes_config_exists():
    assert (ROOT / "sovereign" / "nodes.json").is_file()


def test_route_missing_node_raises(tmp_path):
    import json
    cfg = tmp_path / "nodes.json"
    cfg.write_text("{}")
    from control_plane.integration.route import route
    with pytest.raises(RuntimeError):
        route({"target": "unknown"}, cfg)


def test_route_defaults(tmp_path):
    import json
    cfg = tmp_path / "nodes.json"
    cfg.write_text(json.dumps({"default": {"url": "http://127.0.0.1:1"}}))
    from control_plane.integration.route import route
    r = route({"target": "unknown"}, cfg)
    assert r.status == 0  # unreachable port returns 0
