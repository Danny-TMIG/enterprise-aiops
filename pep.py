class PolicyEnforcementPoint:
    """Policy Enforcement Point (PEP) for validating actor capabilities and risk tiers."""
    def __init__(self, strict_mode=True):
        self.strict_mode = strict_mode
        self.allowed_capabilities = {
            "tier-1": ["execute_pipeline", "write_state", "audit_override"],
            "tier-2": ["read_state", "validate_corpus"],
        }

    def evaluate(self, actor: str, capability: str, risk_tier: str) -> dict:
        tier_caps = self.allowed_capabilities.get(risk_tier, [])
        if capability in tier_caps:
            return {"granted": True, "actor": actor, "tier": risk_tier}
        
        raise PermissionError(f"Access Denied: Actor '{actor}' lacks capability '{capability}' under risk tier '{risk_tier}'.")
