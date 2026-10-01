class VendorProfile:
    def __init__(self, name: str = "default", capabilities: list = None, tier: str = "standard", **kwargs):
        self.name = name
        self.capabilities = capabilities or ["text"]
        self.tier = tier
        for k, v in kwargs.items():
            setattr(self, k, v)

PROFILES = {
    "default": VendorProfile(name="default", capabilities=["text"], tier="standard"),
    "frontier": VendorProfile(name="frontier", capabilities=["text", "reasoning", "multimodal"], tier="enterprise")
}

def get_profile(name: str) -> VendorProfile:
    return PROFILES.get(name, PROFILES.get("default", VendorProfile(name=name)))

def all_profiles() -> list[VendorProfile]:
    return list(PROFILES.values())
