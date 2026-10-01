"""ROB — robotics. Two-link forward kinematics."""
import math
from dcs.generate import requirement

def fk(l1: float, l2: float, t1: float, t2: float) -> tuple[float, float]:
    x = l1*math.cos(t1) + l2*math.cos(t1+t2)
    y = l1*math.sin(t1) + l2*math.sin(t1+t2)
    return x, y

@requirement(id="DCS-ROB-001", title="FK reaches the expected folded pose",
             section="ROB.robotics", hats=["ROB"], criticality="MUST")
def test():
    # Both angles zero → end at (l1 + l2, 0)
    x, y = fk(1.0, 1.0, 0.0, 0.0)
    assert abs(x - 2.0) < 1e-9 and abs(y) < 1e-9

