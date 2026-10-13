"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0200_neg(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0200_neg'}

def impl_genmod_m0200_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0200_max'}

def impl_genmod_m0200_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

RUNNERS = {
    'genmod_m0200_neg': impl_genmod_m0200_neg,
    'genmod_m0200_max': impl_genmod_m0200_max,
    'genmod_m0200_max2': impl_genmod_m0200_max2,
}
