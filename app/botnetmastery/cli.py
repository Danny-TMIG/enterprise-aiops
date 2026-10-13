from __future__ import annotations

import argparse


def main(
argv=None):
    parser = argparse.ArgumentParser(prog="botnetmastery")
    parser.add_argument("command", nargs="?", default="status")
    parser.parse_args(argv)
    return 0


if __name__ == '__main__':
    main()
