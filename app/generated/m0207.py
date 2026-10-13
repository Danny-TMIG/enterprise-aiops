"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0207_identity(a=None, b=None, x=None, xs=None, **kw):
    return x if x is not None else 1

def impl_genmod_m0207_len(a=None, b=None, x=None, xs=None, **kw):
    return len(xs or [1,2,3])

def impl_genmod_m0207_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

def impl_genmod_m0207_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

RUNNERS = {
    'genmod_m0207_identity': impl_genmod_m0207_identity,
    'genmod_m0207_len': impl_genmod_m0207_len,
    'genmod_m0207_min2': impl_genmod_m0207_min2,
    'genmod_m0207_mul': impl_genmod_m0207_mul,
}
