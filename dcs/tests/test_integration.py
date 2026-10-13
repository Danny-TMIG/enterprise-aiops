"""Integration tests that exercise the dcs loader."""
from dcs.self import MANIFESTS, _load_manifest


def test_manifests_exist():
    assert len(MANIFESTS) > 0
    for p in MANIFESTS:
        assert p.exists(), f"missing manifest: {p}"


def test_load_manifest_returns_list_of_dicts():
    data = _load_manifest()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(isinstance(r, dict) for r in data)
    assert all("id" in r for r in data)
