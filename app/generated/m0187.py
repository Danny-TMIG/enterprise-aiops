"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0187_dec(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0187_dec'}

def impl_genmod_m0187_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0187_evens(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0187_evens'}

def impl_genmod_m0187_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0187_min'}

def impl_genmod_m0187_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

def impl_genmod_m0187_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

RUNNERS = {
    'genmod_m0187_dec': impl_genmod_m0187_dec,
    'genmod_m0187_square': impl_genmod_m0187_square,
    'genmod_m0187_evens': impl_genmod_m0187_evens,
    'genmod_m0187_min': impl_genmod_m0187_min,
    'genmod_m0187_max2': impl_genmod_m0187_max2,
    'genmod_m0187_mul': impl_genmod_m0187_mul,
}
