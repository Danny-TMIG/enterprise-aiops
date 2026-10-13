"""Command line interface for CodeQL integration."""

import argparse
import sys

from .runner import CodeQLRunner
from .swarm import CodeQLSwarm


def main(args=None):
    parser = argparse.ArgumentParser(description="Enterprise AIOps CodeQL CLI")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Run CodeQL database creation and analysis")
    analyze_parser.add_argument("--threads", type=int, default=4, help="Number of threads")

    create_parser = subparsers.add_parser("create", help="Create CodeQL database")
    create_parser.add_argument("--language", type=str, default="python", help="Target language")

    subparsers.add_parser("all", help="Run full pipeline")

    parsed_args = parser.parse_args(args)
    runner = CodeQLRunner()

    if parsed_args.cmd == "create":
        success = runner.create_database(language=parsed_args.language)
        sys.exit(0 if success else 1)
    elif parsed_args.cmd == "analyze":
        success = runner.analyze_database(threads=parsed_args.threads)
        sys.exit(0 if success else 1)
    elif parsed_args.cmd == "all":
        swarm = CodeQLSwarm(runner=runner)
        result = swarm.execute_pipeline()
        success = result["database_created"] and result["database_analyzed"]
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
