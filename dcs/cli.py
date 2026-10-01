"""CLI entry point. Delegates to dcs._cli_orig and adds extra subcommands."""

import argparse
import sys

from dcs import _cli_orig


def _coordinate(argv):
    from dcs import team

    fn = getattr(team, "coordinate", None) or getattr(team, "main", None)
    print(fn() if fn else "dcs.team: no entry point")


def _conformance(argv):
    from dcs.tests import conformance as c

    fn = getattr(c, "report", None) or getattr(c, "main", None)
    print(fn() if fn else "dcs.tests.conformance: no entry point")


def _coherence(argv):
    from dcs import coherence

    fn = getattr(coherence, "report", None) or getattr(coherence, "main", None)
    print(fn() if fn else "dcs.coherence: no entry point")


def _balance(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--floor", type=int, default=12)
    a = p.parse_args(argv)
    from dcs import balance

    fn = getattr(balance, "render", None) or getattr(balance, "report", None)
    print(fn(floor=a.floor) if fn else "dcs.balance: no entry point")


def _converge(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--floor", type=int, default=12)
    p.add_argument("--max-steps", type=int, default=40)
    p.add_argument("--write", action="store_true")
    a = p.parse_args(argv)
    from dcs import balance

    fn = getattr(balance, "converge", None)
    print(
        fn(floor=a.floor, max_steps=a.max_steps, write=a.write)
        if fn
        else "dcs.balance: no converge()"
    )


EXTRA = {
    "coordinate": _coordinate,
    "conformance": _conformance,
    "coherence": _coherence,
    "balance": _balance,
    "converge": _converge,
}


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] in EXTRA:
        return EXTRA[argv[0]](argv[1:])
    return _cli_orig.main()


if __name__ == "__main__":
    sys.exit(main())
