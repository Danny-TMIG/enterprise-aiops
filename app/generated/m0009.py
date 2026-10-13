"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0009_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0009_zeroth(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0009_zeroth'}

def impl_genmod_m0009_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0009_max'}

def impl_genmod_m0009_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0009_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

RUNNERS = {
    'genmod_m0009_square': impl_genmod_m0009_square,
    'genmod_m0009_zeroth': impl_genmod_m0009_zeroth,
    'genmod_m0009_max': impl_genmod_m0009_max,
    'genmod_m0009_mul': impl_genmod_m0009_mul,
    'genmod_m0009_max2': impl_genmod_m0009_max2,
}
