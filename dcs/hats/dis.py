"""DIS — distributed. Epidemic gossip converges in O(log n) rounds."""

from dcs.generate import requirement


def converge(peers: dict[str, set[str]], rounds: int = 10) -> set[str]:
    for _ in range(rounds):
        new = {p: set(v) for p, v in peers.items()}
        for p in peers:
            for q in peers[p]:
                new[p] |= peers[q]
        if new == peers:
            return peers[next(iter(peers))]
        peers = new
    return peers[next(iter(peers))]


@requirement(
    id="DCS-DIS-001",
    title="gossip converges to full membership",
    section="DIS.distributed",
    hats=["DIS"],
    criticality="MUST",
)
def test():
    peers = {"a": {"b"}, "b": {"a", "c"}, "c": {"b"}}
    got = converge(peers)
    assert got == {"a", "b", "c"}, got
