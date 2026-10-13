"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0101_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0101_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0101_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0101_min'}

def impl_genmod_m0101_sub(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0101_sub'}

def impl_genmod_m0101_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0101_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

RUNNERS = {
    'genmod_m0101_abs': impl_genmod_m0101_abs,
    'genmod_m0101_square': impl_genmod_m0101_square,
    'genmod_m0101_min': impl_genmod_m0101_min,
    'genmod_m0101_sub': impl_genmod_m0101_sub,
    'genmod_m0101_mul': impl_genmod_m0101_mul,
    'genmod_m0101_max2': impl_genmod_m0101_max2,
}
