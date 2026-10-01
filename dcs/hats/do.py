"""DO — devops. Deployment plan (topological)."""

from dcs.generate import requirement


def plan(services: dict[str, list[str]]) -> list[str]:
    done: set[str] = set()
    order: list[str] = []
    while len(done) < len(services):
        progressed = False
        for svc, deps in services.items():
            if svc in done:
                continue
            if all(d in done for d in deps):
                order.append(svc)
                done.add(svc)
                progressed = True
        if not progressed:
            raise RuntimeError("cycle")
    return order


@requirement(
    id="DCS-DO-001",
    title="deploy plan topo-sorts services",
    section="DO.devops",
    hats=["DO"],
    criticality="MUST",
)
def test():
    svc = {"db": [], "api": ["db"], "web": ["api"]}
    assert plan(svc) == ["db", "api", "web"]
