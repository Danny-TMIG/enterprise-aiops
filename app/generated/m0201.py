"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0201_identity(a=None, b=None, x=None, xs=None, **kw):
    return x if x is not None else 1

def impl_genmod_m0201_len(a=None, b=None, x=None, xs=None, **kw):
    return len(xs or [1,2,3])

def impl_genmod_m0201_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

def impl_genmod_m0201_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0201_sub(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0201_sub'}

RUNNERS = {
    'genmod_m0201_identity': impl_genmod_m0201_identity,
    'genmod_m0201_len': impl_genmod_m0201_len,
    'genmod_m0201_min2': impl_genmod_m0201_min2,
    'genmod_m0201_mul': impl_genmod_m0201_mul,
    'genmod_m0201_sub': impl_genmod_m0201_sub,
}
