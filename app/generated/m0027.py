"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0027_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0027_double'}

def impl_genmod_m0027_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0027_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0027_sort_rev(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0027_sort_rev'}

def impl_genmod_m0027_uniq(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0027_uniq'}

def impl_genmod_m0027_gcd(a=None, b=None, x=None, xs=None, **kw):
    import math; return math.gcd(int(a or 12), int(b or 8))

def impl_genmod_m0027_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

def impl_genmod_m0027_sub(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0027_sub'}

RUNNERS = {
    'genmod_m0027_double': impl_genmod_m0027_double,
    'genmod_m0027_abs': impl_genmod_m0027_abs,
    'genmod_m0027_square': impl_genmod_m0027_square,
    'genmod_m0027_sort_rev': impl_genmod_m0027_sort_rev,
    'genmod_m0027_uniq': impl_genmod_m0027_uniq,
    'genmod_m0027_gcd': impl_genmod_m0027_gcd,
    'genmod_m0027_max2': impl_genmod_m0027_max2,
    'genmod_m0027_sub': impl_genmod_m0027_sub,
}
