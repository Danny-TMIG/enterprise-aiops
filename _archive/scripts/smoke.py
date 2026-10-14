import subprocess
import sys
import time
import urllib.request


def main():
    proc = subprocess.Popen(
        [sys.executable, "-m", "aiops_platform.app.asgi"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(2)
        for url in ("http://127.0.0.1:8000/health", "http://127.0.0.1:8000/"):
            with urllib.request.urlopen(url, timeout=3) as r:
                print(url, "->", r.read().decode())
        return 0
    finally:
        proc.terminate()
        proc.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
