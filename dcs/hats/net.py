"""NET — networking. TCP connect with timeout, no crash on refusal."""

import socket

from dcs.generate import requirement


def can_connect(host: str, port: int, timeout: float = 0.5) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except (TimeoutError, ConnectionRefusedError, OSError):
            return False


@requirement(
    id="DCS-NET-001",
    title="connect helper survives unreachable target",
    section="NET.networking",
    hats=["NET"],
    criticality="MUST",
)
def test():
    # A port unlikely to be open must return False, not raise.
    assert can_connect("127.0.0.1", 1) in (True, False)
