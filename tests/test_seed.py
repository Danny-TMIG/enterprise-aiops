from app.seed.cpvo import CPVOMeter, CPVORecord
from app.seed.manifest import CPVORates, load_manifest


def test_cpvo_measurement():
    rates = CPVORates(rate=2.0)
    meter = CPVOMeter(rates=rates)
    record = CPVORecord(id="test-1", value=5.0)
    assert meter.measure(record) == 10.0

def test_manifest():
    m = load_manifest()
    assert m.version == "1.0"
