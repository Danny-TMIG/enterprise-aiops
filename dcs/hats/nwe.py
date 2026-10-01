"""NWE — net eng. Egress policy allowlist."""
from dcs.generate import requirement

ALLOW = {("127.0.0.1", 8000), ("127.0.0.1", 443), ("::1", 8000)}

def check(host: str, port: int) -> None:
    if (host, port) not in ALLOW:
        raise PermissionError(f"blocked {host}:{port}")

@requirement(id="DCS-NWE-001", title="egress allowlist blocks non-listed targets",
             section="NWE.neteng", hats=["NWE"], criticality="MUST")
def test():
    check("127.0.0.1", 8000)
    try:
        check("8.8.8.8", 53)
    except PermissionError:
        return
    raise AssertionError("egress was not blocked")

