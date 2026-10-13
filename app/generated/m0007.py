"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0007_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0007_neg(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0007_neg'}

def impl_genmod_m0007_zeroth(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0007_zeroth'}

def impl_genmod_m0007_sum(a=None, b=None, x=None, xs=None, **kw):
    return sum(xs or [1,2,3])

def impl_genmod_m0007_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0007_max'}

def impl_genmod_m0007_len(a=None, b=None, x=None, xs=None, **kw):
    return len(xs or [1,2,3])

def impl_genmod_m0007_add(a=None, b=None, x=None, xs=None, **kw):
    return (a or 1) + (b or 2)

def impl_genmod_m0007_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

def impl_genmod_m0007_sub(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0007_sub'}

RUNNERS = {
    'genmod_m0007_abs': impl_genmod_m0007_abs,
    'genmod_m0007_neg': impl_genmod_m0007_neg,
    'genmod_m0007_zeroth': impl_genmod_m0007_zeroth,
    'genmod_m0007_sum': impl_genmod_m0007_sum,
    'genmod_m0007_max': impl_genmod_m0007_max,
    'genmod_m0007_len': impl_genmod_m0007_len,
    'genmod_m0007_add': impl_genmod_m0007_add,
    'genmod_m0007_max2': impl_genmod_m0007_max2,
    'genmod_m0007_sub': impl_genmod_m0007_sub,
}
