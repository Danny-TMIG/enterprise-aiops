"""Moat registry CLI."""
from __future__ import annotations
import argparse, json, sys

from app.atlas.moats import (
    all_moats, by_status, by_implementer, by_residual,
    search, validate, write_markdown, render_markdown,
)


def _hdr(t):
    print("=" * 74)
    print("  " + t)
    print("=" * 74)


def main(
argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="moats")
    parser.add_argument("command", nargs="?", default="status")
    parser.parse_args(argv)
    return 0


if __name__ == '__main__':
    main()
