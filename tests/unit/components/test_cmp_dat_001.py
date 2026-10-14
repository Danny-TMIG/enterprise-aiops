import importlib.util, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "staging",
    ROOT / "components/ac/CMP-DAT-001-data-staging-and-result-collection/src/public/mod001.py",
)
m = importlib.util.module_from_spec(spec); sys.modules["staging"] = m
spec.loader.exec_module(m)


def test_stage_and_collect_round_trip():
    with tempfile.TemporaryDirectory() as td:
        st = m.StagingArea(Path(td))
        a = st.stage(b"hello world", origin="test")
        assert a.size_bytes == 11
        assert st.collect(a.artifact_id) == b"hello world"


def test_content_addressing_dedupes():
    with tempfile.TemporaryDirectory() as td:
        st = m.StagingArea(Path(td))
        a = st.stage(b"same", origin="x")
        b = st.stage(b"same", origin="y")
        assert a.content_hash == b.content_hash
        assert a.artifact_id == b.artifact_id


def test_verify_all_true():
    with tempfile.TemporaryDirectory() as td:
        st = m.StagingArea(Path(td))
        st.stage(b"a", origin="t")
        st.stage(b"b", origin="t")
        assert all(st.verify_all().values())
