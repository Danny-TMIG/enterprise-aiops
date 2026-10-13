"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0140_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0140_identity(a=None, b=None, x=None, xs=None, **kw):
    return x if x is not None else 1

def impl_genmod_m0140_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0140_min'}

def impl_genmod_m0140_uniq(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0140_uniq'}

def impl_genmod_m0140_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

RUNNERS = {
    'genmod_m0140_square': impl_genmod_m0140_square,
    'genmod_m0140_identity': impl_genmod_m0140_identity,
    'genmod_m0140_min': impl_genmod_m0140_min,
    'genmod_m0140_uniq': impl_genmod_m0140_uniq,
    'genmod_m0140_min2': impl_genmod_m0140_min2,
}
