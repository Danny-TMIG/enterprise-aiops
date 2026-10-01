"""Bridges from the fabric to external graph systems.

Each bridge exposes a *model layer* that runs with no external
dependency, plus a *runtime binding* that is honest about what it
requires. `describe()` reports both.
"""
from typing import Any, Dict, List


def describe() -> Dict[str, Any]:
    from app.bridges import uns, ros, ros2, usd
    return {
        "uns":  uns.describe(),
        "ros":  ros.describe(),
        "ros2": ros2.describe(),
        "usd":  usd.describe(),
    }


def _self_register():
    try:
        from app.core.capabilities import register
    except Exception:
        return

    @register("bridges")
    def _entry(*args, **kwargs):
        return describe()


_self_register()
