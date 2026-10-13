"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0086_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0086_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0086_double'}

def impl_genmod_m0086_rev(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0086_rev'}

def impl_genmod_m0086_sum(a=None, b=None, x=None, xs=None, **kw):
    return sum(xs or [1,2,3])

def impl_genmod_m0086_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0086_min'}

def impl_genmod_m0086_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0086_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

def impl_genmod_m0086_sub(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0086_sub'}

RUNNERS = {
    'genmod_m0086_abs': impl_genmod_m0086_abs,
    'genmod_m0086_double': impl_genmod_m0086_double,
    'genmod_m0086_rev': impl_genmod_m0086_rev,
    'genmod_m0086_sum': impl_genmod_m0086_sum,
    'genmod_m0086_min': impl_genmod_m0086_min,
    'genmod_m0086_mul': impl_genmod_m0086_mul,
    'genmod_m0086_max2': impl_genmod_m0086_max2,
    'genmod_m0086_sub': impl_genmod_m0086_sub,
}
