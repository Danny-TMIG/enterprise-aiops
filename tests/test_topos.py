from app.topos import Morphism, Object


def test_category_objects():
    obj_a = Object(name="A")
    obj_b = Object(name="B")
    f = Morphism(source=obj_a, target=obj_b, name="f")
    assert f.source.name == "A"
    assert f.target.name == "B"
