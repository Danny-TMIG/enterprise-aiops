"""Consensus mechanisms in social insects."""

import random  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def bee_waggle(bee_votes: list[float]) -> float:  # pragma: no cover
    """Hive averages dancer-encoded vectors."""
    if not bee_votes:  # pragma: no cover
        return 0.0  # pragma: no cover
    return sum(bee_votes) / len(bee_votes)  # pragma: no cover


def ant_quorum(recruit_rate: float, threshold: int, ticks: int = 200, seed: int = 0) -> dict:  # pragma: no cover
    rng = random.Random(seed)
    recruited = 0
    for _ in range(ticks):
        recruited += int(rng.random() < recruit_rate)
        if recruited >= threshold:  # pragma: no cover
            return {"committed": True, "ticks": _, "recruited": recruited}  # pragma: no cover
    return {"committed": False, "ticks": ticks, "recruited": recruited}  # pragma: no cover


@requirement(
    id="DCS-NAT-CON-001",
    title="hive average equals arithmetic mean",
    section="nature.consensus",
    hats=["DIS", "SCI"],
    criticality="MUST",
)
def test_bee_average():  # pragma: no cover
    assert abs(bee_waggle([1.0, 2.0, 3.0]) - 2.0) < 1e-9


@requirement(
    id="DCS-NAT-CON-002",
    title="quorum commits above threshold",
    section="nature.consensus",
    hats=["DIS", "AUT"],
    criticality="MUST",
)
def test_quorum():  # pragma: no cover
    r = ant_quorum(0.05, threshold=5, seed=1)
    assert r["committed"] and r["recruited"] >= 5
