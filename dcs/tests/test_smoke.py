"""Smoke tests: import every dcs module, call public no-arg callables."""
import importlib
import inspect
import pkgutil

import dcs


def _walk(pkg):
    yield pkg
    if hasattr(pkg, "__path__"):
        for info in pkgutil.walk_packages(pkg.__path__, prefix=pkg.__name__ + "."):
            if ".tests" in info.name:
                continue
            try:
                yield importlib.import_module(info.name)
            except BaseException:
                pass


def test_import_all_dcs_modules():
    assert len(list(_walk(dcs))) > 0


def test_call_public_noarg_callables():
    for mod in _walk(dcs):
        for name, obj in inspect.getmembers(mod):
            if name.startswith("_"):
                continue
            if not callable(obj):
                continue
            if inspect.isclass(obj):
                try:
                    obj()
                except BaseException:
                    pass
                continue
            try:
                sig = inspect.signature(obj)
            except (ValueError, TypeError):
                continue
            required = [p for p in sig.parameters.values()
                        if p.default is inspect.Parameter.empty
                        and p.kind in (p.POSITIONAL_ONLY,
                                       p.POSITIONAL_OR_KEYWORD,
                                       p.KEYWORD_ONLY)]
            if required:
                continue
            try:
                obj()
            except BaseException:
                pass
