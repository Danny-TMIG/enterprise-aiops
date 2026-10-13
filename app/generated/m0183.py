"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0183_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0183_zeroth(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0183_zeroth'}

def impl_genmod_m0183_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0183_double'}

def impl_genmod_m0183_evens(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0183_evens'}

def impl_genmod_m0183_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0183_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

RUNNERS = {
    'genmod_m0183_abs': impl_genmod_m0183_abs,
    'genmod_m0183_zeroth': impl_genmod_m0183_zeroth,
    'genmod_m0183_double': impl_genmod_m0183_double,
    'genmod_m0183_evens': impl_genmod_m0183_evens,
    'genmod_m0183_mul': impl_genmod_m0183_mul,
    'genmod_m0183_max2': impl_genmod_m0183_max2,
}
