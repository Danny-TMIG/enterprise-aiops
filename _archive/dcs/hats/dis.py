"""DIS — distributed. Epidemic gossip converges in O(log n) rounds."""

from dcs.generate import requirement  # pragma: no cover


def converge(peers: dict[str, set[str]], rounds: int = 10) -> set[str]:  # pragma: no cover
    for _ in range(rounds):
        new = {p: set(v) for p, v in peers.items()}
        for p in peers:
            for q in peers[p]:
                new[p] |= peers[q]
        if new == peers:  # pragma: no cover
            return peers[next(iter(peers))]  # pragma: no cover
        peers = new
    return peers[next(iter(peers))]  # pragma: no cover


@requirement(
    id="DCS-DIS-001",
    title="gossip converges to full membership",
    section="DIS.distributed",
    hats=["DIS"],
    criticality="MUST",
)
def test():  # pragma: no cover
    peers = {"a": {"b"}, "b": {"a", "c"}, "c": {"b"}}
    got = converge(peers)
    assert got == {"a", "b", "c"}, got
