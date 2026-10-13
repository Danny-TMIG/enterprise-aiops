"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0137_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0137_inc(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0137_inc'}

def impl_genmod_m0137_identity(a=None, b=None, x=None, xs=None, **kw):
    return x if x is not None else 1

def impl_genmod_m0137_sort(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0137_sort'}

def impl_genmod_m0137_sort_rev(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0137_sort_rev'}

def impl_genmod_m0137_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

def impl_genmod_m0137_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

def impl_genmod_m0137_add(a=None, b=None, x=None, xs=None, **kw):
    return (a or 1) + (b or 2)

RUNNERS = {
    'genmod_m0137_abs': impl_genmod_m0137_abs,
    'genmod_m0137_inc': impl_genmod_m0137_inc,
    'genmod_m0137_identity': impl_genmod_m0137_identity,
    'genmod_m0137_sort': impl_genmod_m0137_sort,
    'genmod_m0137_sort_rev': impl_genmod_m0137_sort_rev,
    'genmod_m0137_min2': impl_genmod_m0137_min2,
    'genmod_m0137_max2': impl_genmod_m0137_max2,
    'genmod_m0137_add': impl_genmod_m0137_add,
}
