"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0165_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0165_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0165_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0165_double'}

def impl_genmod_m0165_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0165_min'}

def impl_genmod_m0165_len(a=None, b=None, x=None, xs=None, **kw):
    return len(xs or [1,2,3])

def impl_genmod_m0165_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0165_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

RUNNERS = {
    'genmod_m0165_square': impl_genmod_m0165_square,
    'genmod_m0165_abs': impl_genmod_m0165_abs,
    'genmod_m0165_double': impl_genmod_m0165_double,
    'genmod_m0165_min': impl_genmod_m0165_min,
    'genmod_m0165_len': impl_genmod_m0165_len,
    'genmod_m0165_mul': impl_genmod_m0165_mul,
    'genmod_m0165_max2': impl_genmod_m0165_max2,
}
