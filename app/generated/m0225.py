"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0225_identity(a=None, b=None, x=None, xs=None, **kw):
    return x if x is not None else 1

def impl_genmod_m0225_neg(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0225_neg'}

def impl_genmod_m0225_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0225_double'}

def impl_genmod_m0225_sort(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0225_sort'}

def impl_genmod_m0225_sort_rev(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0225_sort_rev'}

def impl_genmod_m0225_gcd(a=None, b=None, x=None, xs=None, **kw):
    import math; return math.gcd(int(a or 12), int(b or 8))

def impl_genmod_m0225_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

def impl_genmod_m0225_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

RUNNERS = {
    'genmod_m0225_identity': impl_genmod_m0225_identity,
    'genmod_m0225_neg': impl_genmod_m0225_neg,
    'genmod_m0225_double': impl_genmod_m0225_double,
    'genmod_m0225_sort': impl_genmod_m0225_sort,
    'genmod_m0225_sort_rev': impl_genmod_m0225_sort_rev,
    'genmod_m0225_gcd': impl_genmod_m0225_gcd,
    'genmod_m0225_min2': impl_genmod_m0225_min2,
    'genmod_m0225_max2': impl_genmod_m0225_max2,
}
