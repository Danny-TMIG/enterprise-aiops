"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0104_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0104_sort(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0104_sort'}

def impl_genmod_m0104_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0104_min'}

def impl_genmod_m0104_add(a=None, b=None, x=None, xs=None, **kw):
    return (a or 1) + (b or 2)

def impl_genmod_m0104_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

def impl_genmod_m0104_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

RUNNERS = {
    'genmod_m0104_abs': impl_genmod_m0104_abs,
    'genmod_m0104_sort': impl_genmod_m0104_sort,
    'genmod_m0104_min': impl_genmod_m0104_min,
    'genmod_m0104_add': impl_genmod_m0104_add,
    'genmod_m0104_min2': impl_genmod_m0104_min2,
    'genmod_m0104_max2': impl_genmod_m0104_max2,
}
