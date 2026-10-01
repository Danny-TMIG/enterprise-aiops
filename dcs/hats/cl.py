"""CL — cloud. S3-shaped object store, in-memory backend."""

from dcs.generate import requirement


class ObjectStore:
    def __init__(self):
        self._b: dict[str, bytes] = {}

    def put(self, key: str, data: bytes) -> None:
        self._b[key] = data

    def get(self, key: str) -> bytes:
        return self._b[key]

    def list(self, prefix: str = "") -> list[str]:
        return sorted(k for k in self._b if k.startswith(prefix))


@requirement(
    id="DCS-CL-001",
    title="store does put/get/list with prefixes",
    section="CL.cloud",
    hats=["CL"],
    criticality="MUST",
)
def test():
    s = ObjectStore()
    s.put("runs/0.json", b"a")
    s.put("runs/1.json", b"b")
    s.put("meta.txt", b"c")
    assert s.list("runs/") == ["runs/0.json", "runs/1.json"]
    assert s.get("meta.txt") == b"c"
