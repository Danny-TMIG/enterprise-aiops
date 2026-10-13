"""The shape is verifiable: three adjunctions, one meta-anchor."""
from __future__ import annotations


def test_three_adjunctions():
    from app.shape import ADJUNCTIONS
    assert len(ADJUNCTIONS) == 3
    names = [(a.left_name, a.right_name) for a in ADJUNCTIONS]
    assert ("Integration", "Distribution") in names
    assert ("Distribution", "Experience") in names
    assert ("Experience", "Integration") in names

def test_meta_anchor():
    from app.shape import META_ANCHOR
    assert META_ANCHOR.residual_id == "Ω"
    assert META_ANCHOR.module == "app.residual.terminate"

def test_shape_modules_exist():
    from app.shape import validate
    r = validate()
    assert r["ok"], r

def test_shape_render():
    from app.shape import render
    txt = render()
    assert "Three adjunctions" in txt
    assert "Integration ⊣ Distribution" in txt
    assert "Distribution ⊣ Experience" in txt
    assert "Experience ⊣ Integration" in txt
    assert "Ω" in txt

def test_shape_dict():
    from app.shape import as_dict
    d = as_dict()
    assert len(d["adjunctions"]) == 3
    assert d["meta_anchor"]["residual_id"] == "Ω"

def test_shape_write(tmp_path):
    from app.shape import write_markdown
    p = write_markdown(tmp_path / "shape.md")
    assert p.exists()
    assert "Integration ⊣ Distribution" in p.read_text()
