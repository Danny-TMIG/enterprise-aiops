"""Concurrency: single-flight with deduplication."""

import threading
import time

from dcs.generate import requirement


class SingleFlight:
    def __init__(self):
        self._lock = threading.Lock()
        self._calls = {}

    def do(self, key, fn):
        with self._lock:
            fut = self._calls.get(key)
            if fut is None:
                fut = {"done": False, "value": None, "waiters": []}
                self._calls[key] = fut
                primary = True
            else:
                primary = False
        if primary:
            try:
                fut["value"] = fn()
            finally:
                fut["done"] = True
                with self._lock:
                    self._calls.pop(key, None)
        else:
            while not fut["done"]:
                time.sleep(0.001)
        return fut["value"]


@requirement(
    id="DCS-XC-CONC-001",
    title="single-flight dedupes concurrent calls",
    section="X.concurrency",
    hats=["SYS", "DIS"],
    criticality="MUST",
)
def test():
    sf = SingleFlight()
    calls = {"n": 0}

    def slow():
        calls["n"] += 1
        time.sleep(0.02)
        return 42

    results = []
    threads = [threading.Thread(target=lambda: results.append(sf.do("k", slow))) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert all(r == 42 for r in results)
    assert calls["n"] <= 2, calls["n"]
