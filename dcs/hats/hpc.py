"""HPC — hpc. Bounded thread pool map."""

from concurrent.futures import ThreadPoolExecutor

from dcs.generate import requirement


def pmap(fn, xs, workers: int = 4):
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(fn, xs))


@requirement(
    id="DCS-HPC-001",
    title="parallel map preserves order",
    section="HPC.hpc",
    hats=["HPC"],
    criticality="MUST",
)
def test():
    assert pmap(lambda x: x * x, [1, 2, 3, 4]) == [1, 4, 9, 16]
