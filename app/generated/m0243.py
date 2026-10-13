"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0243_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0243_neg(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0243_neg'}

def impl_genmod_m0243_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0243_min'}

def impl_genmod_m0243_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0243_max'}

def impl_genmod_m0243_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0243_sub(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0243_sub'}

def impl_genmod_m0243_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

RUNNERS = {
    'genmod_m0243_abs': impl_genmod_m0243_abs,
    'genmod_m0243_neg': impl_genmod_m0243_neg,
    'genmod_m0243_min': impl_genmod_m0243_min,
    'genmod_m0243_max': impl_genmod_m0243_max,
    'genmod_m0243_mul': impl_genmod_m0243_mul,
    'genmod_m0243_sub': impl_genmod_m0243_sub,
    'genmod_m0243_min2': impl_genmod_m0243_min2,
}
