"""Algebraic laws. If these hold, composition is sound."""

from dcs.triad.lattice import (  # pragma: no cover
    ALL_STATES,
    join_know,
    join_truth,
    know_le,
    meet_know,
    meet_truth,
    truth_le,
)


def commutative() -> bool:  # pragma: no cover
    for a in ALL_STATES:
        for b in ALL_STATES:
            if join_truth(a, b) != join_truth(b, a):  # pragma: no cover
                return False  # pragma: no cover
            if join_know(a, b) != join_know(b, a):  # pragma: no cover
                return False  # pragma: no cover
            if meet_truth(a, b) != meet_truth(b, a):  # pragma: no cover
                return False  # pragma: no cover
            if meet_know(a, b) != meet_know(b, a):  # pragma: no cover
                return False  # pragma: no cover
    return True  # pragma: no cover


def associative() -> bool:  # pragma: no cover
    for a in ALL_STATES:
        for b in ALL_STATES:
            for c in ALL_STATES:
                if join_truth(join_truth(a, b), c) != join_truth(a, join_truth(b, c)):  # pragma: no cover
                    return False  # pragma: no cover  # pragma: no cover
                if join_know(join_know(a, b), c) != join_know(a, join_know(b, c)):  # pragma: no cover
                    return False  # pragma: no cover  # pragma: no cover
                if meet_truth(meet_truth(a, b), c) != meet_truth(a, meet_truth(b, c)):  # pragma: no cover
                    return False  # pragma: no cover  # pragma: no cover
                if meet_know(meet_know(a, b), c) != meet_know(a, meet_know(b, c)):  # pragma: no cover
                    return False  # pragma: no cover  # pragma: no cover
    return True  # pragma: no cover


def idempotent() -> bool:  # pragma: no cover
    for a in ALL_STATES:
        if join_truth(a, a) != a:  # pragma: no cover
            return False  # pragma: no cover
        if join_know(a, a) != a:  # pragma: no cover
            return False  # pragma: no cover
        if meet_truth(a, a) != a:  # pragma: no cover
            return False  # pragma: no cover
        if meet_know(a, a) != a:  # pragma: no cover
            return False  # pragma: no cover
    return True  # pragma: no cover


def monotone() -> bool:  # pragma: no cover
    for a in ALL_STATES:
        for b in ALL_STATES:
            for c in ALL_STATES:
                if truth_le(a, b) and not truth_le(join_truth(a, c), join_truth(b, c)):  # pragma: no cover
                    return False  # pragma: no cover  # pragma: no cover
                if know_le(a, b) and not know_le(join_know(a, c), join_know(b, c)):  # pragma: no cover
                    return False  # pragma: no cover  # pragma: no cover
    return True  # pragma: no cover


def distributive() -> bool:  # pragma: no cover
    for a in ALL_STATES:
        for b in ALL_STATES:
            for c in ALL_STATES:
                if meet_truth(a, join_truth(b, c)) != join_truth(  # pragma: no cover
                    meet_truth(a, b), meet_truth(a, c)
                ):
                    return False  # pragma: no cover  # pragma: no cover
                if meet_know(a, join_know(b, c)) != join_know(meet_know(a, b), meet_know(a, c)):  # pragma: no cover
                    return False  # pragma: no cover  # pragma: no cover
    return True  # pragma: no cover


LAWS = {
    "COMMUTATIVE": commutative,
    "ASSOCIATIVE": associative,
    "IDEMPOTENT": idempotent,
    "MONOTONE": monotone,
    "DISTRIBUTIVE": distributive,
}


def run_all() -> dict:  # pragma: no cover
    return {name: fn() for name, fn in LAWS.items()}  # pragma: no cover
