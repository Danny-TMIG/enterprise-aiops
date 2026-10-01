from app.autonomy.decisions import Rule, Decision

POLICIES = [
    Rule(
        name="default_allow",
        condition=lambda ctx: True,
        action=lambda ctx: Decision(name="allow", action="proceed"),
        priority=0
    )
]
