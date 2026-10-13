"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0127_inc(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0127_inc'}

def impl_genmod_m0127_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0127_neg(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0127_neg'}

def impl_genmod_m0127_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0127_max'}

def impl_genmod_m0127_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

def impl_genmod_m0127_sub(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0127_sub'}

RUNNERS = {
    'genmod_m0127_inc': impl_genmod_m0127_inc,
    'genmod_m0127_abs': impl_genmod_m0127_abs,
    'genmod_m0127_neg': impl_genmod_m0127_neg,
    'genmod_m0127_max': impl_genmod_m0127_max,
    'genmod_m0127_min2': impl_genmod_m0127_min2,
    'genmod_m0127_sub': impl_genmod_m0127_sub,
}
