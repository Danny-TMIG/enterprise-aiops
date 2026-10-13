"""python3 -m app.shape [--dict|--validate|--write]"""
from __future__ import annotations

import argparse
import json
import sys

from app.shape import as_dict, render, validate, write_markdown


def main(argv=None):
    p = argparse.ArgumentParser(prog="shape")
    p.add_argument("--dict", action="store_true")
    p.add_argument("--validate", action="store_true")
    p.add_argument("--write", action="store_true")
    a = p.parse_args(argv)
    if a.validate:
        print(json.dumps(validate(), indent=2))
        return 0
    if a.dict:
        print(json.dumps(as_dict(), indent=2))
        return 0
    if a.write:
        print(f"  wrote {write_markdown()}")
        return 0
    print(render())
    return 0


if __name__ == "__main__":
    sys.exit(main())
