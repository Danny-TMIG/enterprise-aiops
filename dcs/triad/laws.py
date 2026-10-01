"""Algebraic laws. If these hold, composition is sound."""

from dcs.triad.lattice import (
    ALL_STATES,
    join_know,
    join_truth,
    know_le,
    meet_know,
    meet_truth,
    truth_le,
)


def commutative() -> bool:
    for a in ALL_STATES:
        for b in ALL_STATES:
            if join_truth(a, b) != join_truth(b, a):
                return False
            if join_know(a, b) != join_know(b, a):
                return False
            if meet_truth(a, b) != meet_truth(b, a):
                return False
            if meet_know(a, b) != meet_know(b, a):
                return False
    return True


def associative() -> bool:
    for a in ALL_STATES:
        for b in ALL_STATES:
            for c in ALL_STATES:
                if join_truth(join_truth(a, b), c) != join_truth(a, join_truth(b, c)):
                    return False
                if join_know(join_know(a, b), c) != join_know(a, join_know(b, c)):
                    return False
                if meet_truth(meet_truth(a, b), c) != meet_truth(a, meet_truth(b, c)):
                    return False
                if meet_know(meet_know(a, b), c) != meet_know(a, meet_know(b, c)):
                    return False
    return True


def idempotent() -> bool:
    for a in ALL_STATES:
        if join_truth(a, a) != a:
            return False
        if join_know(a, a) != a:
            return False
        if meet_truth(a, a) != a:
            return False
        if meet_know(a, a) != a:
            return False
    return True


def monotone() -> bool:
    for a in ALL_STATES:
        for b in ALL_STATES:
            for c in ALL_STATES:
                if truth_le(a, b) and not truth_le(join_truth(a, c), join_truth(b, c)):
                    return False
                if know_le(a, b) and not know_le(join_know(a, c), join_know(b, c)):
                    return False
    return True


def distributive() -> bool:
    for a in ALL_STATES:
        for b in ALL_STATES:
            for c in ALL_STATES:
                if meet_truth(a, join_truth(b, c)) != join_truth(
                    meet_truth(a, b), meet_truth(a, c)
                ):
                    return False
                if meet_know(a, join_know(b, c)) != join_know(meet_know(a, b), meet_know(a, c)):
                    return False
    return True


LAWS = {
    "COMMUTATIVE": commutative,
    "ASSOCIATIVE": associative,
    "IDEMPOTENT": idempotent,
    "MONOTONE": monotone,
    "DISTRIBUTIVE": distributive,
}


def run_all() -> dict:
    return {name: fn() for name, fn in LAWS.items()}
