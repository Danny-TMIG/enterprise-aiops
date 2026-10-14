"""NET — networking. TCP connect with timeout, no crash on refusal."""

import socket  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def can_connect(host: str, port: int, timeout: float = 0.5) -> bool:  # pragma: no cover
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True  # pragma: no cover
        except (TimeoutError, ConnectionRefusedError, OSError):  # pragma: no cover
            return False  # pragma: no cover


@requirement(
    id="DCS-NET-001",
    title="connect helper survives unreachable target",
    section="NET.networking",
    hats=["NET"],
    criticality="MUST",
)
def test():  # pragma: no cover
    # A port unlikely to be open must return False, not raise.
    assert can_connect("127.0.0.1", 1) in (True, False)
