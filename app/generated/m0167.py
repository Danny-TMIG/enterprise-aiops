"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0167_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0167_double'}

def impl_genmod_m0167_zeroth(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0167_zeroth'}

def impl_genmod_m0167_identity(a=None, b=None, x=None, xs=None, **kw):
    return x if x is not None else 1

def impl_genmod_m0167_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0167_min'}

def impl_genmod_m0167_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

RUNNERS = {
    'genmod_m0167_double': impl_genmod_m0167_double,
    'genmod_m0167_zeroth': impl_genmod_m0167_zeroth,
    'genmod_m0167_identity': impl_genmod_m0167_identity,
    'genmod_m0167_min': impl_genmod_m0167_min,
    'genmod_m0167_min2': impl_genmod_m0167_min2,
}
