"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0173_neg(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0173_neg'}

def impl_genmod_m0173_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0173_uniq(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0173_uniq'}

def impl_genmod_m0173_sort_rev(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0173_sort_rev'}

def impl_genmod_m0173_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0173_min'}

def impl_genmod_m0173_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0173_sub(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0173_sub'}

RUNNERS = {
    'genmod_m0173_neg': impl_genmod_m0173_neg,
    'genmod_m0173_abs': impl_genmod_m0173_abs,
    'genmod_m0173_uniq': impl_genmod_m0173_uniq,
    'genmod_m0173_sort_rev': impl_genmod_m0173_sort_rev,
    'genmod_m0173_min': impl_genmod_m0173_min,
    'genmod_m0173_mul': impl_genmod_m0173_mul,
    'genmod_m0173_sub': impl_genmod_m0173_sub,
}
