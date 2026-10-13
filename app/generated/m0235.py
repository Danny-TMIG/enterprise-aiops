"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0235_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0235_uniq(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0235_uniq'}

def impl_genmod_m0235_min(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0235_min'}

def impl_genmod_m0235_len(a=None, b=None, x=None, xs=None, **kw):
    return len(xs or [1,2,3])

def impl_genmod_m0235_sub(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0235_sub'}

def impl_genmod_m0235_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

RUNNERS = {
    'genmod_m0235_abs': impl_genmod_m0235_abs,
    'genmod_m0235_uniq': impl_genmod_m0235_uniq,
    'genmod_m0235_min': impl_genmod_m0235_min,
    'genmod_m0235_len': impl_genmod_m0235_len,
    'genmod_m0235_sub': impl_genmod_m0235_sub,
    'genmod_m0235_min2': impl_genmod_m0235_min2,
}
