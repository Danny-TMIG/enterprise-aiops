"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0237_neg(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0237_neg'}

def impl_genmod_m0237_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0237_double'}

def impl_genmod_m0237_identity(a=None, b=None, x=None, xs=None, **kw):
    return x if x is not None else 1

def impl_genmod_m0237_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0237_max'}

def impl_genmod_m0237_odds(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0237_odds'}

def impl_genmod_m0237_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

def impl_genmod_m0237_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0237_add(a=None, b=None, x=None, xs=None, **kw):
    return (a or 1) + (b or 2)

RUNNERS = {
    'genmod_m0237_neg': impl_genmod_m0237_neg,
    'genmod_m0237_double': impl_genmod_m0237_double,
    'genmod_m0237_identity': impl_genmod_m0237_identity,
    'genmod_m0237_max': impl_genmod_m0237_max,
    'genmod_m0237_odds': impl_genmod_m0237_odds,
    'genmod_m0237_max2': impl_genmod_m0237_max2,
    'genmod_m0237_mul': impl_genmod_m0237_mul,
    'genmod_m0237_add': impl_genmod_m0237_add,
}
