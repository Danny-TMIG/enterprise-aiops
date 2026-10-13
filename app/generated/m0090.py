"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0090_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0090_sort(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0090_sort'}

def impl_genmod_m0090_sum(a=None, b=None, x=None, xs=None, **kw):
    return sum(xs or [1,2,3])

def impl_genmod_m0090_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0090_max'}

def impl_genmod_m0090_gcd(a=None, b=None, x=None, xs=None, **kw):
    import math; return math.gcd(int(a or 12), int(b or 8))

def impl_genmod_m0090_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

RUNNERS = {
    'genmod_m0090_abs': impl_genmod_m0090_abs,
    'genmod_m0090_sort': impl_genmod_m0090_sort,
    'genmod_m0090_sum': impl_genmod_m0090_sum,
    'genmod_m0090_max': impl_genmod_m0090_max,
    'genmod_m0090_gcd': impl_genmod_m0090_gcd,
    'genmod_m0090_mul': impl_genmod_m0090_mul,
}
