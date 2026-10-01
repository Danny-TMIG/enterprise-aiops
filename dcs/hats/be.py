"""BE — backend. Typed response envelope."""

from dataclasses import asdict, dataclass
from typing import Any

from dcs.generate import requirement


@dataclass
class Response:
    status: int
    body: Any
    headers: dict

    def to_dict(self):
        return asdict(self)


def health() -> Response:
    return Response(200, {"status": "ok"}, {"content-type": "application/json"})


def not_found(path: str) -> Response:
    return Response(404, {"error": "not_found", "path": path}, {})


@requirement(
    id="DCS-BE-001",
    title="backend returns typed envelope",
    section="BE.backend",
    hats=["BE"],
    criticality="MUST",
)
def test():
    assert health().status == 200
    assert not_found("/x").body["error"] == "not_found"
