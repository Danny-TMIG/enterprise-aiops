"""Moat registry CLI."""
from __future__ import annotations

import argparse


def _hdr(t):
    print("=" * 74)
    print("  " + t)
    print("=" * 74)


def main(
argv=None):
    parser = argparse.ArgumentParser(prog="moats")
    parser.add_argument("command", nargs="?", default="status")
    parser.parse_args(argv)
    return 0


if __name__ == '__main__':
    main()
