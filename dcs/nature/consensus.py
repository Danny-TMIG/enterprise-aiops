"""Consensus mechanisms in social insects."""
import random
from dcs.generate import requirement

def bee_waggle(bee_votes: list[float]) -> float:
    """Hive averages dancer-encoded vectors."""
    if not bee_votes: return 0.0
    return sum(bee_votes) / len(bee_votes)

def ant_quorum(recruit_rate: float, threshold: int, ticks: int = 200,
               seed: int = 0) -> dict:
    rng = random.Random(seed)
    recruited = 0
    for _ in range(ticks):
        recruited += int(rng.random() < recruit_rate)
        if recruited >= threshold:
            return {"committed": True, "ticks": _, "recruited": recruited}
    return {"committed": False, "ticks": ticks, "recruited": recruited}


@requirement(id="DCS-NAT-CON-001", title="hive average equals arithmetic mean",
             section="nature.consensus", hats=["DIS","SCI"], criticality="MUST")
def test_bee_average():
    assert abs(bee_waggle([1.0, 2.0, 3.0]) - 2.0) < 1e-9


@requirement(id="DCS-NAT-CON-002", title="quorum commits above threshold",
             section="nature.consensus", hats=["DIS","AUT"], criticality="MUST")
def test_quorum():
    r = ant_quorum(0.05, threshold=5, seed=1)
    assert r["committed"] and r["recruited"] >= 5
