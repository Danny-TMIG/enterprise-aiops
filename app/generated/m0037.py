"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0037_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0037_double'}

def impl_genmod_m0037_identity(a=None, b=None, x=None, xs=None, **kw):
    return x if x is not None else 1

def impl_genmod_m0037_abs(a=None, b=None, x=None, xs=None, **kw):
    return abs(x if x is not None else -1)

def impl_genmod_m0037_sort(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0037_sort'}

def impl_genmod_m0037_sub(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0037_sub'}

RUNNERS = {
    'genmod_m0037_double': impl_genmod_m0037_double,
    'genmod_m0037_identity': impl_genmod_m0037_identity,
    'genmod_m0037_abs': impl_genmod_m0037_abs,
    'genmod_m0037_sort': impl_genmod_m0037_sort,
    'genmod_m0037_sub': impl_genmod_m0037_sub,
}
