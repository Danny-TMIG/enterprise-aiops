"""HPC — hpc. Bounded thread pool map."""

from concurrent.futures import ThreadPoolExecutor  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


def pmap(fn, xs, workers: int = 4):  # pragma: no cover
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(fn, xs))  # pragma: no cover


@requirement(
    id="DCS-HPC-001",
    title="parallel map preserves order",
    section="HPC.hpc",
    hats=["HPC"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert pmap(lambda x: x * x, [1, 2, 3, 4]) == [1, 4, 9, 16]
