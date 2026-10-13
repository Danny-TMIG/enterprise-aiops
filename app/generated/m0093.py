"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0093_zeroth(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0093_zeroth'}

def impl_genmod_m0093_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0093_evens(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0093_evens'}

def impl_genmod_m0093_odds(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0093_odds'}

def impl_genmod_m0093_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

def impl_genmod_m0093_add(a=None, b=None, x=None, xs=None, **kw):
    return (a or 1) + (b or 2)

RUNNERS = {
    'genmod_m0093_zeroth': impl_genmod_m0093_zeroth,
    'genmod_m0093_square': impl_genmod_m0093_square,
    'genmod_m0093_evens': impl_genmod_m0093_evens,
    'genmod_m0093_odds': impl_genmod_m0093_odds,
    'genmod_m0093_min2': impl_genmod_m0093_min2,
    'genmod_m0093_add': impl_genmod_m0093_add,
}
