from app.moat import score_subsystem


def test_moat_scoring():
    scores = score_subsystem("security")
    assert "security" in scores
