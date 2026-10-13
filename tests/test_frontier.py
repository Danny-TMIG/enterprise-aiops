from app.frontier import get_profile


def test_frontier_profile():
    p = get_profile("default")
    assert p.name == "default"
