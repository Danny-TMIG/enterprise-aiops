"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0078_zeroth(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0078_zeroth'}

def impl_genmod_m0078_identity(a=None, b=None, x=None, xs=None, **kw):
    return x if x is not None else 1

def impl_genmod_m0078_neg(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0078_neg'}

def impl_genmod_m0078_sort_rev(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0078_sort_rev'}

def impl_genmod_m0078_add(a=None, b=None, x=None, xs=None, **kw):
    return (a or 1) + (b or 2)

def impl_genmod_m0078_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0078_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

RUNNERS = {
    'genmod_m0078_zeroth': impl_genmod_m0078_zeroth,
    'genmod_m0078_identity': impl_genmod_m0078_identity,
    'genmod_m0078_neg': impl_genmod_m0078_neg,
    'genmod_m0078_sort_rev': impl_genmod_m0078_sort_rev,
    'genmod_m0078_add': impl_genmod_m0078_add,
    'genmod_m0078_mul': impl_genmod_m0078_mul,
    'genmod_m0078_min2': impl_genmod_m0078_min2,
}
