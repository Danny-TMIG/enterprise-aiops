import subprocess
import sys


def main():
    print("Executing enterprise_aiops test suite...")
    result = subprocess.run(["pytest"], capture_output=False)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
