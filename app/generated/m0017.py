"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0017_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0017_double'}

def impl_genmod_m0017_zeroth(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0017_zeroth'}

def impl_genmod_m0017_uniq(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0017_uniq'}

def impl_genmod_m0017_evens(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0017_evens'}

def impl_genmod_m0017_min2(a=None, b=None, x=None, xs=None, **kw):
    return min(a or 1, b or 2)

RUNNERS = {
    'genmod_m0017_double': impl_genmod_m0017_double,
    'genmod_m0017_zeroth': impl_genmod_m0017_zeroth,
    'genmod_m0017_uniq': impl_genmod_m0017_uniq,
    'genmod_m0017_evens': impl_genmod_m0017_evens,
    'genmod_m0017_min2': impl_genmod_m0017_min2,
}
