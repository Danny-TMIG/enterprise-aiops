import json
from pathlib import Path

def check_structural_equivalence(left: dict, right: dict) -> bool:
    """Verifies behavioral equivalence across two compliance record sets."""
    if left.keys() != right.keys():
        return False
    return all(left[k] == right[k] for k in left)
