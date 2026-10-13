from app.autonomy import Decision, DecisionEngine, Rule


def test_decision_engine():
    engine = DecisionEngine()
    rule = Rule(name="test_rule", condition=lambda ctx: ctx.get("run") is True, action=lambda ctx: Decision(name="ok", action="go"))
    engine.add_rule(rule)
    res = engine.evaluate({"run": True})
    assert res.action == "go"
