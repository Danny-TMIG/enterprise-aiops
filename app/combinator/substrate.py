"""Substrate abstraction.

The six rules are the same on every substrate. The substrate
determines only how the graph is stored and how the next active
pair is found. The semantics of the reduction are identical.

We provide:

  - RAMSubstrate: in-memory dict (the default).
  - StreamingSubstrate: externalises the graph to disk between
    steps to demonstrate that no continuous RAM residency is
    required.
  - A Substrate Protocol so that FPGA / GPU / ASIC backends can
    be dropped in with the same six rules.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Protocol

from app.combinator.graph import Graph
from app.combinator.reduce import normalise, step


class Substrate(Protocol):
    name: str
    def normalise(self, g: Graph,
                  max_steps: int = 10_000) -> tuple[Graph, int, bool]:
        ...


# ── CPU / in-memory ─────────────────────────────────────────────
class RAMSubstrate:
    name = "ram"

    def normalise(self, g: Graph, max_steps: int = 10_000):
        return normalise(g, max_steps=max_steps)


# ── Streaming / disk-backed ─────────────────────────────────────
class StreamingSubstrate:
    name = "streaming"

    def __init__(self, scratch: Path | None = None):
        self.scratch = Path(scratch) if scratch else Path(
            tempfile.mkdtemp(prefix="ic_stream_"))

    def _write(self, g: Graph, path: Path) -> None:
        doc = {
            "nodes": {str(k): v for k, v in g.nodes.items()},
            "wires": {f"{a[0]}:{a[1]}": [b[0], b[1]]
                      for a, b in g.wires.items()},
            "next_id": g._next_id,
        }
        path.write_text(json.dumps(doc))

    def _read(self, path: Path) -> Graph:
        doc = json.loads(path.read_text())
        g = Graph()
        g.nodes = {int(k): v for k, v in doc["nodes"].items()}
        g.wires = {}
        for k, v in doc["wires"].items():
            a0, a1 = k.split(":")
            g.wires[(int(a0), int(a1))] = (v[0], v[1])
        g._next_id = doc["next_id"]
        return g

    def normalise(self, g: Graph, max_steps: int = 10_000):
        """Reduce with the graph externalised between steps.
        At no point does the caller hold the full graph in RAM
        except transiently inside a single step."""
        path = self.scratch / "graph.json"
        self._write(g, path)
        n = 0
        while n < max_steps:
            g_local = self._read(path)
            fired = step(g_local)
            self._write(g_local, path)
            if not fired:
                return self._read(path), n, True
            n += 1
        return self._read(path), n, False
