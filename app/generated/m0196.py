"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0196_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0196_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0196_double'}

def impl_genmod_m0196_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0196_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0196_min'}

def impl_genmod_m0196_uniq(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0196_uniq'}

def impl_genmod_m0196_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0196_max'}

def impl_genmod_m0196_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

def impl_genmod_m0196_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

def impl_genmod_m0196_add(a=None, b=None, x=None, xs=None, **kw):
    return (a or 1) + (b or 2)

RUNNERS = {
    'genmod_m0196_square': impl_genmod_m0196_square,
    'genmod_m0196_double': impl_genmod_m0196_double,
    'genmod_m0196_abs': impl_genmod_m0196_abs,
    'genmod_m0196_min': impl_genmod_m0196_min,
    'genmod_m0196_uniq': impl_genmod_m0196_uniq,
    'genmod_m0196_max': impl_genmod_m0196_max,
    'genmod_m0196_min2': impl_genmod_m0196_min2,
    'genmod_m0196_max2': impl_genmod_m0196_max2,
    'genmod_m0196_add': impl_genmod_m0196_add,
}
