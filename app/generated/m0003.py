"""Auto-generated from capabilities DB."""
from __future__ import annotations


def impl_genmod_m0003_double(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0003_double'}

def impl_genmod_m0003_max(a=None, b=None, x=None, xs=None, **kw):
    return {'ok': True, 'code': 'genmod_m0003_max'}

def impl_genmod_m0003_max2(a=None, b=None, x=None, xs=None, **kw):
    return max(a or 1, b or 2)

RUNNERS = {
    'genmod_m0003_double': impl_genmod_m0003_double,
    'genmod_m0003_max': impl_genmod_m0003_max,
    'genmod_m0003_max2': impl_genmod_m0003_max2,
}
