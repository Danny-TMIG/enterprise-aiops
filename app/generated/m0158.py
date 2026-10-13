"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0158_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0158_dec(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0158_dec'}

def impl_genmod_m0158_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0158_max'}

def impl_genmod_m0158_rev(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0158_rev'}

def impl_genmod_m0158_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

RUNNERS = {
    'genmod_m0158_abs': impl_genmod_m0158_abs,
    'genmod_m0158_dec': impl_genmod_m0158_dec,
    'genmod_m0158_max': impl_genmod_m0158_max,
    'genmod_m0158_rev': impl_genmod_m0158_rev,
    'genmod_m0158_min2': impl_genmod_m0158_min2,
}
