from __future__ import annotations
import argparse, json, sys
from pathlib import Path

from app.botnetmastery.c2 import C2Server
from app.botnetmastery.simulation import Simulation


def main(
argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="botnetmastery")
    parser.add_argument("command", nargs="?", default="status")
    parser.parse_args(argv)
    return 0


if __name__ == '__main__':
    main()
