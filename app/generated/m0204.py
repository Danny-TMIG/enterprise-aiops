"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0204_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0204_neg(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0204_neg'}

def impl_genmod_m0204_sum(a=None, b=None, x=None, xs=None, **kw):
    return sum(xs or [1,2,3])

def impl_genmod_m0204_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

RUNNERS = {
    'genmod_m0204_square': impl_genmod_m0204_square,
    'genmod_m0204_neg': impl_genmod_m0204_neg,
    'genmod_m0204_sum': impl_genmod_m0204_sum,
    'genmod_m0204_min2': impl_genmod_m0204_min2,
}
