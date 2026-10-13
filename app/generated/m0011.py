"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0011_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0011_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0011_max'}

def impl_genmod_m0011_uniq(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0011_uniq'}

def impl_genmod_m0011_len(a=None, b=None, x=None, xs=None, **kw):
    return len(xs or [1,2,3])

def impl_genmod_m0011_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

def impl_genmod_m0011_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

def impl_genmod_m0011_gcd(a=None, b=None, x=None, xs=None, **kw):
    import math; return math.gcd(int(a or 12), int(b or 8))

RUNNERS = {
    'genmod_m0011_abs': impl_genmod_m0011_abs,
    'genmod_m0011_max': impl_genmod_m0011_max,
    'genmod_m0011_uniq': impl_genmod_m0011_uniq,
    'genmod_m0011_len': impl_genmod_m0011_len,
    'genmod_m0011_mul': impl_genmod_m0011_mul,
    'genmod_m0011_min2': impl_genmod_m0011_min2,
    'genmod_m0011_gcd': impl_genmod_m0011_gcd,
}
