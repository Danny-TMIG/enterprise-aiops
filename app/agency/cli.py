"""Demonstrate the four primitives anchored to the live mesh.

The mesh supplies the subjects (nodes). The registry supplies the
records. The gate returns a Decision using the atlas's own
RESULT STATES.
"""
from __future__ import annotations

import hashlib


def _h(*p: str) -> str:
    m = hashlib.sha256()
    for s in p:
        m.update(s.encode()); m.update(b"\x1f")
    return "sha256:" + m.hexdigest()


def _live_mesh_nodes(limit: int = 6):
    try:
        from app.mesh.runtime import get_mesh
        m = get_mesh()
        return list(m.graph.nodes.values())[:limit]
    except Exception as e:
        print(f"  ! mesh unavailable: {e}")
        return []


def main(
argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="agency")
    parser.add_argument("command", nargs="?", default="status")
    parser.parse_args(argv)
    return 0


if __name__ == '__main__':
    main()
