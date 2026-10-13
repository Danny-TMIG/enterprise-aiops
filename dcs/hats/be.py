"""BE — backend. Typed response envelope."""

from dataclasses import asdict, dataclass  # pragma: no cover
from typing import Any  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


@dataclass
class Response:  # pragma: no cover
    status: int
    body: Any
    headers: dict

    def to_dict(self):  # pragma: no cover
        return asdict(self)  # pragma: no cover


def health() -> Response:  # pragma: no cover
    return Response(200, {"status": "ok"}, {"content-type": "application/json"})  # pragma: no cover


def not_found(path: str) -> Response:  # pragma: no cover
    return Response(404, {"error": "not_found", "path": path}, {})  # pragma: no cover


@requirement(
    id="DCS-BE-001",
    title="backend returns typed envelope",
    section="BE.backend",
    hats=["BE"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert health().status == 200
    assert not_found("/x").body["error"] == "not_found"
