"""Claim 4: nothing was fetched from the network at runtime.

Method: ban the outbound socket functions (create_connection,
getaddrinfo, gethostbyname, gethostbyaddr) in-process. Leave
socket.socket and socket.socketpair alone so imports work. Force
HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE so the loader is cache-only.
Run a full grammar -> swarm -> refine -> ast.parse pipeline.
"""
from __future__ import annotations

import os
import socket
import sys
import traceback


class _Blocked(RuntimeError):
    pass


def _ban(*a, **k):
    raise _Blocked("outbound network blocked at runtime")


OUTBOUND = [
    "create_connection", "getaddrinfo", "gethostbyname",
    "gethostbyname_ex", "gethostbyaddr", "getnameinfo",
]


def main() -> int:
    print("-- claim 4: no outbound network at runtime --")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    saved = {n: getattr(socket, n) for n in OUTBOUND}
    for n in OUTBOUND:
        setattr(socket, n, _ban)

    try:
        import ast

        from app.origami.dispatch import dispatch, refine
        from app.origami.library import get as get_grammar
        from app.origami.swarm import Swarm

        g = get_grammar("code_artifact")
        s = Swarm(n_workers=1)
        r = dispatch(g, s, seed=1, max_depth=6, max_tokens=32)

        if "dry-run" in r.code or "[dry-run:" in r.code:
            print("  FAIL  swarm produced dry-run output — model not "
                  "loaded under socket ban")
            return 1

        ast.parse(r.code)
        r.code = refine(r.code, s, max_tokens=128)
        ast.parse(r.code)
        print(f"  PASS  pipeline ran fully offline "
              f"({len(r.code)} chars, ast.parse twice)")
        return 0
    except _Blocked as e:
        print(f"  FAIL  outbound network attempted: {e}")
        return 1
    except Exception as e:
        print(f"  FAIL  {type(e).__name__}: {e}")
        traceback.print_exc()
        return 1
    finally:
        for n, fn in saved.items():
            setattr(socket, n, fn)


if __name__ == "__main__":
    sys.exit(main())
