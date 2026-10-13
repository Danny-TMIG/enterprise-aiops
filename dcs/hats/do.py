"""DO — devops. Deployment plan (topological)."""

from dcs.generate import requirement  # pragma: no cover


def plan(services: dict[str, list[str]]) -> list[str]:  # pragma: no cover
    done: set[str] = set()
    order: list[str] = []
    while len(done) < len(services):
        progressed = False
        for svc, deps in services.items():
            if svc in done:  # pragma: no cover
                continue
            if all(d in done for d in deps):  # pragma: no cover
                order.append(svc)
                done.add(svc)
                progressed = True
        if not progressed:  # pragma: no cover
            raise RuntimeError("cycle")  # pragma: no cover
    return order  # pragma: no cover


@requirement(
    id="DCS-DO-001",
    title="deploy plan topo-sorts services",
    section="DO.devops",
    hats=["DO"],
    criticality="MUST",
)
def test():  # pragma: no cover
    svc = {"db": [], "api": ["db"], "web": ["api"]}
    assert plan(svc) == ["db", "api", "web"]
