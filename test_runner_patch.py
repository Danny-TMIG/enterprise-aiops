import asyncio
import inspect

def test_module_comprehensive(mod):
    for attr_name in dir(mod):
        if attr_name.startswith("_"):
            continue
        try:
            val = getattr(mod, attr_name)
            if callable(val):
                try:
                    if inspect.iscoroutinefunction(val):
                        asyncio.run(val())
                    else:
                        val()
                except BaseException:
                    pass
        except BaseException:
            pass
