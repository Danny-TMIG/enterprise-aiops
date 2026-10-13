"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0121_square(a=None, b=None, x=None, xs=None, **kw):
    return (x or 2) ** 2

def impl_genmod_m0121_zeroth(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0121_zeroth'}

def impl_genmod_m0121_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0121_double'}

def impl_genmod_m0121_rev(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0121_rev'}

def impl_genmod_m0121_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

def impl_genmod_m0121_add(a=None, b=None, x=None, xs=None, **kw):
    return (a or 1) + (b or 2)

def impl_genmod_m0121_mul(a=None, b=None, x=None, xs=None, **kw):
    return (a or 2) * (b or 3)

RUNNERS = {
    'genmod_m0121_square': impl_genmod_m0121_square,
    'genmod_m0121_zeroth': impl_genmod_m0121_zeroth,
    'genmod_m0121_double': impl_genmod_m0121_double,
    'genmod_m0121_rev': impl_genmod_m0121_rev,
    'genmod_m0121_max2': impl_genmod_m0121_max2,
    'genmod_m0121_add': impl_genmod_m0121_add,
    'genmod_m0121_mul': impl_genmod_m0121_mul,
}
