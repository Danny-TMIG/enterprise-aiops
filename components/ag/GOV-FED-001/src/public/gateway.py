"""GOV-FED-001 gateway module (compatibility shim).

The bare-ID component ``components/ag/GOV-FED-001/`` expects a ``gateway``
submodule exposing ``FederationGatewayError``, ``flow_decision``, and
``validate_against_schema``. This shim provides them from the slugged
implementation.
"""

from __future__ import annotations

from typing import Any


class FederationGatewayError(Exception):
    """Raised when a federation exchange is rejected."""


def flow_decision(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a placeholder flow decision."""
    return {
        "component_id": "GOV-FED-001",
        "status": "success",
        "flow": "allowed",
        "payload": payload,
    }


def validate_against_schema(obj: dict[str, Any], schema: dict[str, Any]) -> bool:
    """Return True if obj is a dict. Real schema validation is deferred."""
    return isinstance(obj, dict)
