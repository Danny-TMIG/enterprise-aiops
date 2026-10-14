"""CL — cloud. S3-shaped object store, in-memory backend."""

from dcs.generate import requirement  # pragma: no cover


class ObjectStore:  # pragma: no cover
    def __init__(self):  # pragma: no cover
        self._b: dict[str, bytes] = {}

    def put(self, key: str, data: bytes) -> None:  # pragma: no cover
        self._b[key] = data

    def get(self, key: str) -> bytes:  # pragma: no cover
        return self._b[key]  # pragma: no cover

    def list(self, prefix: str = "") -> list[str]:  # pragma: no cover
        return sorted(k for k in self._b if k.startswith(prefix))  # pragma: no cover


@requirement(
    id="DCS-CL-001",
    title="store does put/get/list with prefixes",
    section="CL.cloud",
    hats=["CL"],
    criticality="MUST",
)
def test():  # pragma: no cover
    s = ObjectStore()
    s.put("runs/0.json", b"a")
    s.put("runs/1.json", b"b")
    s.put("meta.txt", b"c")
    assert s.list("runs/") == ["runs/0.json", "runs/1.json"]
    assert s.get("meta.txt") == b"c"
