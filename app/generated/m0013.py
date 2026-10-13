"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0013_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0013_double'}

def impl_genmod_m0013_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0013_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0013_min'}

def impl_genmod_m0013_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0013_max'}

def impl_genmod_m0013_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

RUNNERS = {
    'genmod_m0013_double': impl_genmod_m0013_double,
    'genmod_m0013_abs': impl_genmod_m0013_abs,
    'genmod_m0013_min': impl_genmod_m0013_min,
    'genmod_m0013_max': impl_genmod_m0013_max,
    'genmod_m0013_min2': impl_genmod_m0013_min2,
}
