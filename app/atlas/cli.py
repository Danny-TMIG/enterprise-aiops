"""Live doc CLI: regenerate, query, validate."""
from __future__ import annotations

import argparse


def _hdr(t: str) -> None:
    print("=" * 72)
    print("  " + t)
    print("=" * 72)


def main(
argv=None):
    parser = argparse.ArgumentParser(prog="atlas")
    parser.add_argument("command", nargs="?", default="list")
    parser.parse_args(argv)
    return 0


if __name__ == '__main__':
    main()
