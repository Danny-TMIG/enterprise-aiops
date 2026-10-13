"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0060_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0060_neg(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0060_neg'}

def impl_genmod_m0060_zeroth(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0060_zeroth'}

def impl_genmod_m0060_evens(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0060_evens'}

def impl_genmod_m0060_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0060_max'}

def impl_genmod_m0060_odds(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0060_odds'}

def impl_genmod_m0060_gcd(a=None, b=None, x=None, xs=None, **kw):
    import math; return math.gcd(int(a or 12), int(b or 8))

RUNNERS = {
    'genmod_m0060_abs': impl_genmod_m0060_abs,
    'genmod_m0060_neg': impl_genmod_m0060_neg,
    'genmod_m0060_zeroth': impl_genmod_m0060_zeroth,
    'genmod_m0060_evens': impl_genmod_m0060_evens,
    'genmod_m0060_max': impl_genmod_m0060_max,
    'genmod_m0060_odds': impl_genmod_m0060_odds,
    'genmod_m0060_gcd': impl_genmod_m0060_gcd,
}
