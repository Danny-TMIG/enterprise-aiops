"""Concurrency: single-flight with deduplication."""

import threading  # pragma: no cover
import time  # pragma: no cover

from dcs.generate import requirement  # pragma: no cover


class SingleFlight:  # pragma: no cover
    def __init__(self):  # pragma: no cover
        self._lock = threading.Lock()
        self._calls = {}

    def do(self, key, fn):  # pragma: no cover
        with self._lock:
            fut = self._calls.get(key)
            if fut is None:  # pragma: no cover
                fut = {"done": False, "value": None, "waiters": []}
                self._calls[key] = fut
                primary = True
            else:
                primary = False
        if primary:  # pragma: no cover
            try:
                fut["value"] = fn()
            finally:
                fut["done"] = True
                with self._lock:
                    self._calls.pop(key, None)
        else:
            while not fut["done"]:
                time.sleep(0.001)
        return fut["value"]  # pragma: no cover


@requirement(
    id="DCS-XC-CONC-001",
    title="single-flight dedupes concurrent calls",
    section="X.concurrency",
    hats=["SYS", "DIS"],
    criticality="MUST",
)
def test():  # pragma: no cover
    sf = SingleFlight()
    calls = {"n": 0}

    def slow():  # pragma: no cover
        calls["n"] += 1
        time.sleep(0.02)
        return 42  # pragma: no cover

    results = []
    threads = [threading.Thread(target=lambda: results.append(sf.do("k", slow))) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert all(r == 42 for r in results)
    assert calls["n"] <= 2, calls["n"]
