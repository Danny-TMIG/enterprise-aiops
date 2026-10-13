"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0036_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0036_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0036_sort_rev(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0036_sort_rev'}

def impl_genmod_m0036_sort(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0036_sort'}

def impl_genmod_m0036_add(a=None, b=None, x=None, xs=None, **kw):
    return (a or 1) + (b or 2)

def impl_genmod_m0036_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

RUNNERS = {
    'genmod_m0036_square': impl_genmod_m0036_square,
    'genmod_m0036_abs': impl_genmod_m0036_abs,
    'genmod_m0036_sort_rev': impl_genmod_m0036_sort_rev,
    'genmod_m0036_sort': impl_genmod_m0036_sort,
    'genmod_m0036_add': impl_genmod_m0036_add,
    'genmod_m0036_min2': impl_genmod_m0036_min2,
}
