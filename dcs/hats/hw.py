"""HW — hardware. Budget descriptor + fit test."""

from dcs.generate import requirement  # pragma: no cover

HW = {"cpu_cores": 12, "unified_mem_gb": 64, "platform": "apple_m4_max"}


def fits(need: dict) -> bool:  # pragma: no cover
    return need.get("cores", 0) <= HW["cpu_cores"] and need.get("mem_gb", 0) <= HW["unified_mem_gb"]  # pragma: no cover


@requirement(
    id="DCS-HW-001",
    title="hardware fit honors core and memory ceilings",
    section="HW.hardware",
    hats=["HW"],
    criticality="MUST",
)
def test():  # pragma: no cover
    assert fits({"cores": 4, "mem_gb": 16})
    assert not fits({"cores": 32, "mem_gb": 16})
    assert not fits({"cores": 4, "mem_gb": 128})
