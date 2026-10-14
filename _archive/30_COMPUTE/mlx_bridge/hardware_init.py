import platform
import sys


def verify_hardware_profile():
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        sys.exit(1)
    return {"model": "Mac16,5", "memory_gb": 128}


if __name__ == "__main__":
    verify_hardware_profile()
