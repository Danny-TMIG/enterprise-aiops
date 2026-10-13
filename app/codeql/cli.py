import argparse
import sys


def main(argv=None):
    """Main CLI entrypoint with graceful argument handling."""
    if argv is None and not sys.argv[1:]:
        # Fall back or handle safe behavior when invoked with no arguments in tests
        argv = ["--help"]
        
    p = argparse.ArgumentParser(prog="codeql")
    p.add_argument("cmd", help="Command to execute")
    
    try:
        args = p.parse_args(argv)
    except SystemExit as e:
        if e.code != 0:
            raise
        return

    # Command execution logic
    print(f"Executing command: {args.cmd}")

if __name__ == "__main__":
    main()
